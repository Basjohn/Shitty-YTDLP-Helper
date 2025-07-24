import PyInstaller.__main__
import os
import shutil
import platform

def clean_build():
    # Clean up previous builds
    for item in ['build', 'dist', 'ShittyYTDLPHelper.spec']:
        if os.path.isdir(item):
            shutil.rmtree(item)
        elif os.path.exists(item):
            os.remove(item)

def build():
    clean_build()
    
    # PyInstaller configuration
    app_name = 'ShittyYTDLPHelper'
    script = 'shitty_ytdlphelper.py'
    
    # Use appropriate icon file based on platform
    is_windows = platform.system() == 'Windows'
    icon_ext = 'ico' if is_windows else 'png'
    icon = f'SYHS.{icon_ext}'
    
    # PyInstaller arguments
    args = [
        script,
        '--name=%s' % app_name,
        '--onefile',
        '--windowed',
        '--icon=%s' % icon,
        f'--add-data={icon}:.',
        '--noconsole',
        '--clean',
        '--log-level=INFO'
    ]
    
    # Platform-specific adjustments
    if not is_windows:
        # On Linux, we need to use a different path separator and add the icon
        args = [arg.replace(';', ':') for arg in args]
        # Add additional data files if needed for Linux
        args.append('--add-data=shitty-ytdlp-helper.desktop:.')
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # Verify the executable was created
    exe_ext = '.exe' if is_windows else ''
    exe_name = f"{app_name}{exe_ext}"
    exe_path = os.path.join('dist', exe_name)
    
    if os.path.exists(exe_path):
        print(f"\n✅ Build successful!")
        print(f"Executable created at: {os.path.abspath(exe_path)}")
        print(f"Size: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
        
        # Additional Linux-specific instructions
        if not is_windows:
            print("\nTo make the application available system-wide:")
            print(f"1. Make the binary executable:")
            print(f"   chmod +x {os.path.abspath(exe_path)}")
            print("2. Install the desktop file:")
            print("   mkdir -p ~/.local/share/applications/")
            print("   cp shitty-ytdlp-helper.desktop ~/.local/share/applications/")
    else:
        print("\n❌ Build failed - executable not found in dist directory")
        print("Please check the build output for errors.")

if __name__ == '__main__':
    print("Starting build process...")
    build()
