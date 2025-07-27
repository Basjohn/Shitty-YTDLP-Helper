import PyInstaller.__main__
import os
import shutil
import sys
from pathlib import Path

def clean_build():
    """Clean up previous build artifacts."""
    build_artifacts = ['build', 'dist', 'ShittyYTDLPHelper.spec']
    for item in build_artifacts:
        if os.path.isdir(item):
            print(f"Removing directory: {item}")
            shutil.rmtree(item, ignore_errors=True)
        elif os.path.exists(item):
            print(f"Removing file: {item}")
            os.remove(item)

def get_resource_files(rc_dir):
    """Get all resource files from the rc directory."""
    resource_files = []
    if os.path.exists(rc_dir):
        for root, _, files in os.walk(rc_dir):
            for file in files:
                if not file.startswith('.'):  # Skip hidden files
                    src_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, os.path.dirname(os.path.abspath(__file__)))
                    resource_files.append((src_path, rel_path))
    return resource_files

def build():
    """Build the ShittyYTDLPHelper executable."""
    try:
        clean_build()
        
        # Configuration
        app_name = 'ShittyYTDLPHelper'
        script = 'shitty_ytdlphelper.py'
        version = '1.1Two'
        
        # Paths
        base_dir = Path(__file__).parent
        rc_dir = base_dir / 'rc'
        icon = str(rc_dir / 'SYHSB.ico')
        
        # Get all resource files
        resource_files = get_resource_files(rc_dir)
        
        # Build PyInstaller arguments
        args = [
            script,
            f'--name={app_name}',
            '--onefile',
            '--windowed',
            f'--icon={icon}',
            '--noconsole',
            '--clean',
            '--log-level=INFO',
            f'--version-file=version.txt',
            '--add-binary=yt-dlp.exe;.' if os.path.exists('yt-dlp.exe') else ''
        ]
        
        # Add resource files
        for src, dst in resource_files:
            if os.path.exists(src):
                args.append(f'--add-data={src}{os.pathsep}{dst}')
        
        # Filter out any empty arguments
        args = [arg for arg in args if arg]
        
        print("Starting build with the following arguments:")
        print(' '.join(args))
        
        # Run PyInstaller
        PyInstaller.__main__.run(args)
        
        # Verify the executable was created
        exe_path = os.path.join('dist', f"{app_name}.exe")
        if os.path.exists(exe_path):
            # Set file version information
            try:
                import pywintypes
                from win32com.shell import shell, shellcon
                
                # Get the file version info
                info = shell.SHGetFileInfo(exe_path, 0, shellcon.SHGFI_DISPLAYNAME | shellcon.SHGFI_TYPENAME)
                
                # Set version info
                exe_path_abs = os.path.abspath(exe_path)
                shell.SHSetFileInfo(
                    exe_path_abs,
                    0,
                    shellcon.SHGFI_DISPLAYNAME | shellcon.SHGFI_TYPENAME,
                    f"Shitty YTDLP Helper v{version}",
                    "Application"
                )
                print(f"\n✅ Version info set to: {version}")
            except Exception as e:
                print(f"\n⚠️ Could not set version info: {e}")
            
            print(f"\n✅ Build successful!")
            print(f"Executable: {os.path.abspath(exe_path)}")
            print(f"Size: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
            return True
        else:
            print("\n❌ Build failed - executable not found in dist directory")
            return False
            
    except Exception as e:
        print(f"\n❌ Build failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_version_file():
    """Create a version file for the executable."""
    version = '1.1Two'
    version_content = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers=(1, 1, 2, 0),
    prodvers=(1, 1, 2, 0),
    # Contains a bitmask that specifies the valid bits 'flags'
    mask=0x3f,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x40004,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'Shitty Software'),
        StringStruct('FileDescription', 'Shitty YTDLP Helper'),
        StringStruct('FileVersion', '{0}'),
        StringStruct('InternalName', 'ShittyYTDLPHelper'),
        StringStruct('LegalCopyright', '© 2023 Shitty Software. All rights reserved.'),
        StringStruct('OriginalFilename', 'ShittyYTDLPHelper.exe'),
        StringStruct('ProductName', 'Shitty YTDLP Helper'),
        StringStruct('ProductVersion', '{0}')])
      ]), 
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""".format(version, version)

    with open('version.txt', 'w', encoding='utf-8') as f:
        f.write(version_content)

if __name__ == '__main__':
    print(f"Building Shitty YTDLP Helper v1.1Two")
    print("-" * 50)
    
    # Create version file
    create_version_file()
    
    # Run the build
    success = build()
    
    # Clean up
    if os.path.exists('version.txt'):
        os.remove('version.txt')
    
    # Exit with appropriate status
    sys.exit(0 if success else 1)
