from http.server import BaseHTTPRequestHandler
import os
import json
from supabase import create_client, Client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Obtener configuraciones de múltiples proyectos Supabase
            projects_json = os.environ.get('SUPABASE_PROJECTS', '{}')
            projects = json.loads(projects_json)
            
            results = []
            
            for project_name, config in projects.items():
                try:
                    url = config.get('url')
                    key = config.get('key')
                    table = config.get('table', 'users')  # Tabla por defecto
                    
                    if not url or not key:
                        results.append({
                            'project': project_name,
                            'status': 'error',
                            'message': 'Missing URL or key'
                        })
                        continue
                    
                    # Crear cliente de Supabase
                    supabase: Client = create_client(url, key)
                    
                    # Hacer una consulta simple para mantener la DB activa
                    response = supabase.table(table).select('*', count='exact').limit(1).execute()
                    
                    results.append({
                        'project': project_name,
                        'status': 'success',
                        'message': f'Database kept alive successfully',
                        'count': response.count if hasattr(response, 'count') else 'N/A'
                    })
                    
                except Exception as e:
                    results.append({
                        'project': project_name,
                        'status': 'error',
                        'message': str(e)
                    })
            
            # Respuesta exitosa
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'results': results
            }, indent=2).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': str(e)
            }).encode())

