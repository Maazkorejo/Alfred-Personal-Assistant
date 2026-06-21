import subprocess
import json


def find_installed_app(query: str):
    """
    Search all installed Start Menu apps (regular + UWP) for a name match.
    Returns the AppID/path if found, else None.
    """
    try:
        ps_command = (
            "Get-StartApps | ConvertTo-Json"
        )
        result = subprocess.run(
            ['powershell', '-Command', ps_command],
            capture_output=True, text=True, timeout=10
        )
        apps = json.loads(result.stdout)

        # Get-StartApps returns a list, but if only 1 app exists it might return a dict
        if isinstance(apps, dict):
            apps = [apps]

        query_lower = query.lower().strip()

        # Exact match first
        for app in apps:
            if app['Name'].lower() == query_lower:
                return app

        # Partial match fallback
        for app in apps:
            if query_lower in app['Name'].lower():
                return app

        return None

    except Exception:
        return None


def open_app(app_name: str) -> dict:
    """
    Open any installed desktop or UWP application by searching Windows' app list.
    """
    try:
        app = find_installed_app(app_name)

        if app:
            app_id = app['AppID']
            subprocess.Popen(f'explorer.exe shell:AppsFolder\\{app_id}', shell=True)
            return {'success': True, 'app': app['Name']}

        # Fallback: try launching as a raw .exe (covers some edge cases Get-StartApps misses)
        query = app_name.lower().strip().replace(' ', '')
        try:
            subprocess.Popen(f'{query}.exe', shell=True)
            return {'success': True, 'app': app_name}
        except Exception:
            pass

        return {'success': False, 'error': f"Could not find '{app_name}' installed on this system."}

    except Exception as e:
        return {'success': False, 'error': str(e)}

import os


def open_path(path: str) -> dict:
    """
    Open a file or folder using the default Windows handler.
    Accepts absolute paths like C:\\Users\\maazk\\Desktop or a file path.
    """
    try:
        clean_path = path.strip().strip('"').strip("'")

        if not os.path.exists(clean_path):
            return {'success': False, 'error': f"Path not found: {clean_path}"}

        os.startfile(clean_path)
        return {'success': True, 'path': clean_path}

    except Exception as e:
        return {'success': False, 'error': str(e)}       