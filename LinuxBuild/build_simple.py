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
    
    # Set up paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Platform-specific settings
    is_windows = platform.system() == 'Windows'
    icon_ext = 'ico' if is_windows else 'png'
    icon_name = 'SYHSB'
    
    # Source and destination paths for rc directory
    rc_dir = os.path.join(base_dir, 'rc')
    if not os.path.exists(rc_dir):
        os.makedirs(rc_dir, exist_ok=True)
    
    # Ensure the icon exists in the rc directory
    src_icon = os.path.join(rc_dir, f'{icon_name}.{icon_ext}')
    if not os.path.exists(src_icon):
        # Try to find the icon in the base directory as fallback
        fallback_icon = os.path.join(base_dir, f'{icon_name}.{icon_ext}')
        if os.path.exists(fallback_icon):
            shutil.copy2(fallback_icon, src_icon)
        else:
            raise FileNotFoundError(f"Icon not found at: {src_icon} or {fallback_icon}")
    
    # PyInstaller arguments
    args = [
        script,
        '--name=%s' % app_name,
        '--onefile',
        '--windowed',
        '--noconsole',
        '--clean',
        '--log-level=INFO',
        '--add-binary=yt-dlp:.'  # Include yt-dlp in the build
    ]
    
    # Add icon and rc directory
    if os.path.exists(rc_dir):
        args.extend([
            f'--icon={src_icon}',
            f'--add-data={src_icon}{os.pathsep}rc',
            f'--add-data={os.path.join(rc_dir, "SYHSB.png")}{os.pathsep}rc',
            f'--add-data={os.path.join(rc_dir, "SYHSB.ico")}{os.pathsep}rc'
        ])
    
    # Platform-specific adjustments
    if not is_windows:
        # On Linux, we need to use a different path separator
        args = [arg.replace(';', ':') for arg in args]
        # Add .desktop file for Linux
        desktop_file = os.path.join(build_dir, 'shitty-ytdlp-helper.desktop')
        if os.path.exists(desktop_file):
            args.append(f'--add-data={desktop_file}:.')
        
        # Include ffmpeg if available
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            args.append(f'--add-binary={ffmpeg_path}:.')
    
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
            print("2. Install the desktop file and icon:")
            print("   mkdir -p ~/.local/share/applications/")
            print("   mkdir -p ~/.local/share/icons/hicolor/256x256/apps/")
            print("   cp shitty-ytdlp-helper.desktop ~/.local/share/applications/")
            print("   cp rc/SYHSB.png ~/.local/share/icons/hicolor/256x256/apps/SYHSB.png")
            print("   update-desktop-database ~/.local/share/applications")
            print("   gtk-update-icon-cache ~/.local/share/icons/hicolor -f")
    else:
        print("\n❌ Build failed - executable not found in dist directory")
        print("Please check the build output for errors.")

if __name__ == '__main__':
    print("Starting build process...")
    build()
