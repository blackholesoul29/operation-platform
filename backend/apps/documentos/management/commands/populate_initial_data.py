from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Populates initial data: TipoDocumento, DocumentoRequerido, and admin user'

    def handle(self, *args, **options):
        from apps.documentos.models import TipoDocumento, DocumentoRequerido
        from apps.users.models import UserProfile

        self.stdout.write('Creando tipos de documento...')

        tipos_data = [
            {'nombre': 'RUT', 'codigo': 'rut', 'tiene_vencimiento': False,
             'descripcion': 'Registro Único Tributario'},
            {'nombre': 'CERL - Certificado de Existencia y Representación Legal',
             'codigo': 'cerl', 'tiene_vencimiento': True,
             'descripcion': 'Certificado de Existencia y Representación Legal'},
            {'nombre': 'Certificado Bancario', 'codigo': 'cert_bancario',
             'tiene_vencimiento': True, 'descripcion': 'Certificado de cuenta bancaria'},
            {'nombre': 'Cédula Representante Legal', 'codigo': 'cedula_rl',
             'tiene_vencimiento': False, 'descripcion': 'Cédula de ciudadanía del representante legal'},
            {'nombre': 'Información del Proyecto', 'codigo': 'info_proyecto',
             'tiene_vencimiento': False, 'descripcion': 'Información técnica y comercial del proyecto'},
            {'nombre': 'Coordenadas del Proyecto', 'codigo': 'coordenadas',
             'tiene_vencimiento': False, 'descripcion': 'Coordenadas geográficas del proyecto'},
            {'nombre': 'NDA Firmado', 'codigo': 'nda',
             'tiene_vencimiento': False, 'descripcion': 'Acuerdo de no divulgación firmado'},
            {'nombre': 'Oferta Comercial', 'codigo': 'oferta_comercial',
             'tiene_vencimiento': False, 'descripcion': 'Oferta comercial enviada al cliente'},
            {'nombre': 'Contrato Firmado', 'codigo': 'contrato_firmado',
             'tiene_vencimiento': False, 'descripcion': 'Contrato firmado por ambas partes'},
            {'nombre': 'Acta de Inicio', 'codigo': 'acta_inicio',
             'tiene_vencimiento': False, 'descripcion': 'Acta de inicio del proyecto'},
            {'nombre': 'Info Energía Requerida / RECs', 'codigo': 'info_recs',
             'tiene_vencimiento': False, 'descripcion': 'Información sobre energía requerida y RECs'},
        ]

        tipos = {}
        for data in tipos_data:
            obj, created = TipoDocumento.objects.get_or_create(
                codigo=data['codigo'],
                defaults={
                    'nombre': data['nombre'],
                    'tiene_vencimiento': data['tiene_vencimiento'],
                    'descripcion': data['descripcion'],
                }
            )
            tipos[data['codigo']] = obj
            status_str = 'creado' if created else 'ya existía'
            self.stdout.write(f"  TipoDocumento '{data['nombre']}': {status_str}")

        self.stdout.write('\nCreando documentos requeridos por servicio...')

        requeridos_data = [
            # Representación de Frontera
            ('representacion', 'rut', True),
            ('representacion', 'cerl', True),
            ('representacion', 'cert_bancario', True),
            ('representacion', 'info_proyecto', True),
            # CGM
            ('cgm', 'rut', True),
            ('cgm', 'cerl', True),
            ('cgm', 'cert_bancario', True),
            ('cgm', 'info_proyecto', True),
            # Monitoreo
            ('monitoreo', 'rut', True),
            ('monitoreo', 'cerl', True),
            ('monitoreo', 'cert_bancario', True),
            ('monitoreo', 'info_proyecto', True),
            # PPA
            ('ppa', 'rut', True),
            ('ppa', 'cerl', True),
            ('ppa', 'cedula_rl', True),
            ('ppa', 'cert_bancario', True),
            ('ppa', 'coordenadas', True),
            ('ppa', 'info_proyecto', True),
            # RECs
            ('recs', 'cerl', True),
            ('recs', 'info_recs', True),
        ]

        for servicio, codigo, obligatorio in requeridos_data:
            tipo_doc = tipos.get(codigo)
            if not tipo_doc:
                self.stdout.write(self.style.WARNING(f"  Tipo documento '{codigo}' no encontrado, saltando..."))
                continue
            obj, created = DocumentoRequerido.objects.get_or_create(
                servicio=servicio,
                tipo_documento=tipo_doc,
                defaults={'obligatorio': obligatorio}
            )
            status_str = 'creado' if created else 'ya existía'
            self.stdout.write(f"  DocumentoRequerido {servicio} / {codigo}: {status_str}")

        self.stdout.write('\nCreando usuario administrador...')

        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@enerflow.co',
                'first_name': 'Admin',
                'last_name': 'EnerFlow',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(f"  Usuario admin creado con contraseña 'admin123'")
        else:
            self.stdout.write(f"  Usuario admin ya existía")

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = 'admin'
        profile.save()

        self.stdout.write(self.style.SUCCESS('\n¡Datos iniciales cargados correctamente!'))
