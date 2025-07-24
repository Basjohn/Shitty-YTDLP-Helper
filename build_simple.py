import PyInstaller.__main__
import os
import shutil

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
    
    # Path to resources
    rc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rc')
    icon = os.path.join(rc_dir, 'SYHSB.ico')
    png_icon = os.path.join(rc_dir, 'SYHSB.png')
    
    # Ensure rc directory exists
    if not os.path.exists(rc_dir):
        os.makedirs(rc_dir, exist_ok=True)
    
    # Check for required files
    required_files = [icon, png_icon]
    for file in required_files:
        if not os.path.exists(file):
            raise FileNotFound(f"Required file not found: {file}")
    
    # PyInstaller arguments
    args = [
        script,
        '--name=%s' % app_name,
        '--onefile',
        '--windowed',
        f'--icon={icon}',
        # Include all necessary files in the rc directory
        f'--add-data={icon};rc',
        f'--add-data={png_icon};rc',
        # Include yt-dlp if it exists
        '--add-binary=yt-dlp.exe;.',
        '--noconsole',
        '--clean',
        '--log-level=INFO',
        # Ensure the rc directory is included in the binary
        '--add-data=rc;rc'
    ]
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    # Verify the executable was created
    exe_path = os.path.join('dist', f"{app_name}.exe")
    if os.path.exists(exe_path):
        print(f"\n✅ Build successful!")
        print(f"Executable created at: {os.path.abspath(exe_path)}")
        print(f"Size: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
    else:
        print("\n❌ Build failed - executable not found in dist directory")
        print("Please check the build output for errors.")

if __name__ == '__main__':
    print("Starting build process...")
    build()
