"""
Group Change Params Client
Main entry point for the PyQt6 application
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main function to start the application"""
    
    print("🚀 Starting Group Change Params Client...")
    
    # Check working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Working directory: {script_dir}")
    
    try:
        print("📦 Importing PyQt5...")
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from PyQt5.QtCore import Qt
        print("✅ PyQt5 imported successfully")
        
        print("📦 Importing main window...")
        from gui.main_window import GroupChangeParamsWindow
        print("✅ Main window imported successfully")
        
        print("🎯 Creating application...")
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Group Change Params")
        app.setOrganizationName("Altawin Extensions")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        print("🖥️  Creating main window...")
        # Create and show main window
        window = GroupChangeParamsWindow()
        print("✅ Main window created successfully")
        
        # Handle command line order ID argument
        if len(sys.argv) > 1:
            try:
                order_id = int(sys.argv[1])
                print(f"📋 Setting order ID from command line: {order_id}")
                window.set_order_id(order_id)
            except ValueError:
                print("⚠️  Invalid order ID format in command line arguments")
        
        print("📺 Showing window...")
        # Show window
        window.show()
        
        print("▶️  Starting application...")
        # Start application
        sys.exit(app.exec())
        
    except ImportError as e:
        error_msg = f"Import error: {e}"
        print(f"❌ {error_msg}")
        print("💡 Possible solutions:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Activate virtual environment")
        print("   3. Check that PyQt5 is installed: pip install PyQt5")
        
        # Show MessageBox if possible
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication([])
            QMessageBox.critical(None, "Startup Error", error_msg + 
                               "\n\nInstall dependencies:\npip install -r requirements.txt")
        except:
            pass
            
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Critical error: {e}"
        print(f"❌ {error_msg}")
        print("📋 Error details:")
        import traceback
        traceback.print_exc()
        
        # Show MessageBox if possible
        try:
            from PyQt5.QtWidgets import QApplication, QMessageBox
            app = QApplication([])
            QMessageBox.critical(None, "Critical Error", 
                               error_msg + "\n\nCheck console for details")
        except:
            pass
            
        print("\n💡 Try:")
        print("   1. Check that the API server is running")
        print("   2. Reinstall dependencies")
        print("   3. Check the error messages above")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
