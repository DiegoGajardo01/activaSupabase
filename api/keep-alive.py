from http.server import BaseHTTPRequestHandler
import os
import json
from supabase import create_client, Client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Obtener configuraciones de múltiples proyectos Supabase
            projects_json = os.environ.get('SUPABASE_PROJECTS', '{}')
            
            # Limpiar el JSON por si tiene caracteres extraños
            projects_json = projects_json.strip()
            
            # Intentar parsear el JSON
            try:
                projects = json.loads(projects_json)
            except json.JSONDecodeError as json_err:
                # Si falla, intentar con mejor manejo de errores
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': f'Invalid JSON format in SUPABASE_PROJECTS: {str(json_err)}',
                    'hint': 'Make sure the JSON is valid and on a single line, or properly escaped'
                }).encode())
                return
            
            if not isinstance(projects, dict) or len(projects) == 0:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'SUPABASE_PROJECTS must be a non-empty JSON object'
                }).encode())
                return
            
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
                    
                    # Intentar hacer una consulta simple para mantener la DB activa
                    # Si la tabla especificada no existe, intentar con tablas comunes
                    success = False
                    error_message = None
                    tables_tried = []
                    
                    # Lista de tablas a intentar (primero la especificada, luego comunes)
                    tables_to_try = [table, 'users', 'profiles', 'public.users']
                    
                    for try_table in tables_to_try:
                        if try_table in tables_tried:
                            continue
                        try:
                            tables_tried.append(try_table)
                            # Intentar obtener el count correcto
                            count_value = None
                            
                            # Método más confiable: hacer una consulta con count='exact' sin limit
                            try:
                                count_query = supabase.table(try_table).select('*', count='exact').limit(0)
                                count_response = count_query.execute()
                                
                                # Intentar usar el método interno para obtener el count desde headers
                                if hasattr(count_response, '_get_count_from_content_range_header'):
                                    try:
                                        count_value = count_response._get_count_from_content_range_header()
                                    except:
                                        pass
                                
                                # Si no funcionó, usar el atributo count directamente
                                if (count_value is None or count_value == 0) and hasattr(count_response, 'count'):
                                    count_value = count_response.count
                                    
                            except Exception as e:
                                # Si falla, continuamos sin count
                                pass
                            
                            # Si aún no tenemos count, hacer una consulta simple para activar la DB
                            # y contar manualmente los resultados (limitado a 1000)
                            if count_value is None or count_value == 0:
                                try:
                                    data_response = supabase.table(try_table).select('*').limit(1000).execute()
                                    if hasattr(data_response, 'data'):
                                        manual_count = len(data_response.data)
                                        if manual_count == 1000:
                                            count_value = "1000+ (limitado)"
                                        elif manual_count > 0:
                                            count_value = manual_count
                                        else:
                                            # Si el count es 0, puede ser por RLS (Row Level Security)
                                            # La consulta funciona pero no devuelve datos visibles
                                            count_value = "0 (RLS activo)"
                                except:
                                    pass
                            
                            # Hacer una consulta final para asegurar que la DB está activa
                            response = supabase.table(try_table).select('*').limit(1).execute()
                            
                            success = True
                            results.append({
                                'project': project_name,
                                'status': 'success',
                                'message': f'Database kept alive successfully',
                                'table_used': try_table,
                                'count': count_value if count_value is not None else 'N/A'
                            })
                            break
                        except Exception as table_err:
                            error_message = str(table_err)
                            # Si es error de tabla no encontrada, intentar siguiente
                            if 'PGRST205' in str(table_err) or 'not find the table' in str(table_err).lower():
                                continue
                            else:
                                # Si es otro tipo de error, parar
                                break
                    
                    # Si ninguna tabla funcionó, al menos intentamos conectar
                    if not success:
                        # Como último recurso, intentar una consulta RPC simple o verificar conexión
                        try:
                            # Intentar obtener información básica de la conexión
                            # Esto activará la DB aunque no haya tabla disponible
                            supabase.table('_realtime').select('*').limit(0).execute()
                            results.append({
                                'project': project_name,
                                'status': 'warning',
                                'message': f'Connection successful but no accessible tables found. Tables tried: {", ".join(tables_tried)}',
                                'error': error_message
                            })
                        except:
                            results.append({
                                'project': project_name,
                                'status': 'error',
                                'message': f'Could not connect or query database. Tables tried: {", ".join(tables_tried)}',
                                'error': error_message
                            })
                    
                except Exception as e:
                    results.append({
                        'project': project_name,
                        'status': 'error',
                        'message': f'Connection error: {str(e)}'
                    })
            
            # Respuesta exitosa (aunque algunos proyectos puedan haber fallado)
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

