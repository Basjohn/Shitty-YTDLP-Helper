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
    icon = 'SYHS.ico'
    
    # PyInstaller arguments
    args = [
        script,
        '--name=%s' % app_name,
        '--onefile',
        '--windowed',
        '--icon=%s' % icon,
        '--add-data=SYHS.ico;.',
        '--noconsole',
        '--clean',
        '--log-level=INFO'
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
