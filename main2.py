import os
import struct
import subprocess
import tempfile
import shutil
import argparse
import hexdump
from pathlib import Path
from typing import Optional

try:
    from dissect.cstruct import cstruct
    from dissect.volume.vhd import VHD
    DISSECT_AVAILABLE = True
except ImportError:
    DISSECT_AVAILABLE = False


class VHDCreator:
    """VHDファイルを作成し、ファイルを追加する"""
    
    def __init__(self, vhd_path: str, size_mb: int = 100):
        """
        VHDファイルを初期化
        
        Args:
            vhd_path: VHDファイルの出力パス
            size_mb: VHDサイズ（MB）
        """
        self.vhd_path = Path(vhd_path)
        self.size_mb = size_mb
        self.size_bytes = size_mb * 1024 * 1024
        
    def create_vhd(self):
        """VHDファイルを作成"""
        print(f"Creating VHD file: {self.vhd_path}")
        
        # VHDファイルを作成（ダイナミックVHD形式）
        with open(self.vhd_path, 'wb') as f:
            # VHDボディ（スパースファイル）
            f.write(b'\x00' * self.size_bytes)
        
        print(f"VHD file created: {self.vhd_path} ({self.size_mb}MB)")
        
    def create_filesystem(self):
        """VHD内にファイルシステムを作成"""
        print(f"Creating filesystem in VHD...")
        
        # ループデバイスをセットアップ
        result = subprocess.run(
            ['sudo', 'losetup', '-f', str(self.vhd_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        
        loop_device = result.stdout.strip()
        print(f"Loop device: {loop_device}")
        
        try:
            # ext4ファイルシステムを作成
            result = subprocess.run(
                ['sudo', 'mkfs.ext4', '-F', loop_device],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"Error creating filesystem: {result.stderr}")
                return False
            
            print("Filesystem created successfully")
            return True
        finally:
            # ループデバイスをデタッチ
            subprocess.run(['sudo', 'losetup', '-d', loop_device])
    
    def mount_vhd(self, mount_point: str):
        """VHDをマウント"""
        mount_path = Path(mount_point)
        mount_path.mkdir(parents=True, exist_ok=True)
        
        # ループデバイスをセットアップ
        result = subprocess.run(
            ['sudo', 'losetup', '-f', str(self.vhd_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        
        loop_device = result.stdout.strip()
        print(f"Using loop device: {loop_device}")
        
        # マウント
        result = subprocess.run(
            ['sudo', 'mount', loop_device, str(mount_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Mount error: {result.stderr}")
            subprocess.run(['sudo', 'losetup', '-d', loop_device])
            return None
        
        print(f"VHD mounted at: {mount_path}")
        return loop_device
    
    def unmount_vhd(self, mount_point: str, loop_device: str):
        """VHDをアンマウント"""
        subprocess.run(['sudo', 'umount', str(mount_point)])
        subprocess.run(['sudo', 'losetup', '-d', loop_device])
        print(f"VHD unmounted from: {mount_point}")
    
    def add_text_file(self, file_path: str, content: str):
        """
        VHD内にテキストファイルを追加
        
        Args:
            file_path: VHD内のファイルパス（例：/test.txt）
            content: ファイルの内容
        """
        mount_point = tempfile.mkdtemp(prefix='vhd_mount_')
        
        try:
            # VHDをマウント
            loop_device = self.mount_vhd(mount_point)
            if not loop_device:
                print("Failed to mount VHD")
                return False
            
            # ファイルを書き込み
            file_full_path = os.path.join(mount_point, file_path.lstrip('/'))
            os.makedirs(os.path.dirname(file_full_path), exist_ok=True)
            
            with open(file_full_path, 'w') as f:
                f.write(content)
            
            print(f"File added to VHD: {file_path}")
            
            # アンマウント
            self.unmount_vhd(mount_point, loop_device)
            return True
        
        except Exception as e:
            print(f"Error: {e}")
            return False
        
        finally:
            # 一時ディレクトリを削除
            if os.path.exists(mount_point):
                shutil.rmtree(mount_point)
    
    def inspect_vhd(self):
        """dissectを使用してVHDファイルを検査"""
        if not DISSECT_AVAILABLE:
            print("Error: dissect not installed. Install with: uv pip install dissect.cstruct dissect.volume")
            return False
        
        try:
            with open(self.vhd_path, 'rb') as f:
                vhd = VHD(f)
                
                print(f"\n{'='*60}")
                print(f"VHD File Information: {self.vhd_path}")
                print(f"{'='*60}")
                
                # VHDヘッダ情報
                header = vhd.header
                print(f"\nHeader Information:")
                print(f"  Signature: {header.signature}")
                print(f"  Features: 0x{header.features:08x}")
                print(f"  File Format Version: {header.file_format_version}")
                print(f"  Data Offset: {header.data_offset}")
                print(f"  Timestamp: {header.timestamp}")
                print(f"  Creator Version: {header.creator_version}")
                print(f"  Creator Host OS: {header.creator_host_os}")
                print(f"  Original Size: {header.original_size} bytes ({header.original_size / (1024**2):.2f} MB)")
                print(f"  Current Size: {header.current_size} bytes ({header.current_size / (1024**2):.2f} MB)")
                print(f"  Disk Geometry: {header.geometry}")
                print(f"  Disk Type: {header.disk_type}")
                print(f"  Checksum: 0x{header.checksum:08x}")
                
                # フッタ情報
                footer = vhd.footer
                print(f"\nFooter Information:")
                print(f"  Signature: {footer.signature}")
                print(f"  Is Fixed: {footer.features & 0x2 != 0}")
                
                print(f"\n{'='*60}\n")
                return True
        
        except Exception as e:
            print(f"Error inspecting VHD: {e}")
            return False
    
    def hex_dump_vhd(self, num_bytes: int = 512):
        """VHDファイルのヘックスダンプを表示"""
        try:
            with open(self.vhd_path, 'rb') as f:
                data = f.read(num_bytes)
                
                print(f"\n{'='*60}")
                print(f"VHD File Hex Dump (first {num_bytes} bytes): {self.vhd_path}")
                print(f"{'='*60}\n")
                
                hexdump.hexdump(data)
                
                print(f"\n{'='*60}\n")
                return True
        
        except Exception as e:
            print(f"Error reading VHD: {e}")
            return False


def main():
    """コマンドラインインターフェース"""
    parser = argparse.ArgumentParser(
        description="VHD File Creator - VHDファイルの作成と管理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # VHDファイルを作成
  uv run main.py create -s 100 myfile.vhd

  # ファイルシステムを作成
  uv run main.py create-fs myfile.vhd

  # テキストファイルをVHDに追加
  uv run main.py add-file myfile.vhd /hello.txt "Hello World"

  # ファイルパスから追加
  uv run main.py add-file myfile.vhd /data.txt --input data.txt

  # VHDをマウント
  uv run main.py mount myfile.vhd /mnt/vhd

  # VHDをアンマウント
  uv run main.py unmount /mnt/vhd <loop_device>

  # VHDファイルを検査（dissect）
  uv run main.py inspect myfile.vhd

  # VHDファイルのヘックスダンプ
  uv run main.py hex-dump myfile.vhd
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='コマンド')
    
    # create: VHDファイル作成
    create_parser = subparsers.add_parser('create', help='VHDファイルを作成')
    create_parser.add_argument('vhd_path', help='VHDファイルパス')
    create_parser.add_argument('-s', '--size', type=int, default=100, help='サイズ（MB、デフォルト: 100）')
    
    # create-fs: ファイルシステム作成
    createfs_parser = subparsers.add_parser('create-fs', help='VHD内にファイルシステムを作成')
    createfs_parser.add_argument('vhd_path', help='VHDファイルパス')
    
    # add-file: ファイル追加
    addfile_parser = subparsers.add_parser('add-file', help='VHDにテキストファイルを追加')
    addfile_parser.add_argument('vhd_path', help='VHDファイルパス')
    addfile_parser.add_argument('file_path', help='VHD内のファイルパス（例：/hello.txt）')
    addfile_parser.add_argument('content', nargs='?', default=None, help='ファイル内容')
    addfile_parser.add_argument('-i', '--input', help='ファイルから読み込み')
    
    # mount: マウント
    mount_parser = subparsers.add_parser('mount', help='VHDをマウント')
    mount_parser.add_argument('vhd_path', help='VHDファイルパス')
    mount_parser.add_argument('mount_point', help='マウントポイント')
    
    # unmount: アンマウント
    unmount_parser = subparsers.add_parser('unmount', help='VHDをアンマウント')
    unmount_parser.add_argument('mount_point', help='マウントポイント')
    unmount_parser.add_argument('loop_device', help='ループデバイス（例：/dev/loop0）')
    
    # inspect: VHDファイル検査
    inspect_parser = subparsers.add_parser('inspect', help='VHDファイルを検査（dissect使用）')
    inspect_parser.add_argument('vhd_path', help='VHDファイルパス')
    
    # hex-dump: ヘックスダンプ
    hexdump_parser = subparsers.add_parser('hex-dump', help='VHDファイルのヘックスダンプを表示')
    hexdump_parser.add_argument('vhd_path', help='VHDファイルパス')
    hexdump_parser.add_argument('-n', '--num-bytes', type=int, default=512, help='表示バイト数（デフォルト: 512）')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # create コマンド
    if args.command == 'create':
        creator = VHDCreator(args.vhd_path, size_mb=args.size)
        creator.create_vhd()
    
    # create-fs コマンド
    elif args.command == 'create-fs':
        creator = VHDCreator(args.vhd_path)
        if creator.create_filesystem():
            print("✓ Filesystem created successfully")
        else:
            print("✗ Failed to create filesystem")
    
    # add-file コマンド
    elif args.command == 'add-file':
        content = None
        
        if args.input:
            # ファイルから読み込み
            try:
                with open(args.input, 'r') as f:
                    content = f.read()
                print(f"Read from: {args.input}")
            except FileNotFoundError:
                print(f"Error: File not found: {args.input}")
                return
        elif args.content:
            content = args.content
        else:
            print("Error: Content or --input option required")
            return
        
        creator = VHDCreator(args.vhd_path)
        if creator.add_text_file(args.file_path, content):
            print(f"✓ File added to VHD: {args.file_path}")
        else:
            print("✗ Failed to add file to VHD")
    
    # mount コマンド
    elif args.command == 'mount':
        creator = VHDCreator(args.vhd_path)
        loop_device = creator.mount_vhd(args.mount_point)
        if loop_device:
            print(f"✓ Mounted at: {args.mount_point}")
            print(f"✓ Loop device: {loop_device}")
            print(f"Unmount with: uv run main.py unmount {args.mount_point} {loop_device}")
        else:
            print("✗ Failed to mount VHD")
    
    # unmount コマンド
    elif args.command == 'unmount':
        creator = VHDCreator("")
        creator.unmount_vhd(args.mount_point, args.loop_device)
        print(f"✓ Unmounted: {args.mount_point}")
    
    # inspect コマンド
    elif args.command == 'inspect':
        creator = VHDCreator(args.vhd_path)
        if creator.inspect_vhd():
            print("✓ VHD inspection completed")
        else:
            print("✗ Failed to inspect VHD")
    
    # hex-dump コマンド
    elif args.command == 'hex-dump':
        creator = VHDCreator(args.vhd_path)
        if creator.hex_dump_vhd(args.num_bytes):
            print("✓ Hex dump completed")
        else:
            print("✗ Failed to create hex dump")


if __name__ == "__main__":
    main()
