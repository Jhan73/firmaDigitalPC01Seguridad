import os
from cryptography.hazmat.primitives.serialization import pkcs12
import endesive.pdf
import datetime

def cargar_certificado(pkcs12_path, password):
    try:
        with open(pkcs12_path, "rb") as file:
            pkcs12_data = file.read()
        private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
            pkcs12_data, password.encode()
        )
        return private_key, certificate, additional_certificates
    except Exception as e:
        print(f"Error al cargar el certificado {pkcs12_path}: {e}")
        return None, None, None

def firmar_pdf(input_pdf, output_pdf, private_key, certificate, additional_certificates, contact, location, reason):
    try:
        date = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
        dct = {
            "sigflags": 3,
            "contact": contact,
            "location": location,
            "signingdate": date.strftime("%Y%m%d%H%M%S+00'00'"),
            "reason": reason,
            "signature": "Por los puntos",
        }
        with open(input_pdf, "rb") as f:
            pdf_data = f.read()

        signature = endesive.pdf.cms.sign(pdf_data, dct, private_key, certificate, additional_certificates)
        
        with open(output_pdf, "wb") as f:
            f.write(pdf_data)
            f.write(signature)
        print(f"PDF firmado guardado como: {output_pdf}")
    
    except Exception as e:
        print(f"Error al firmar el PDF {input_pdf}: {e}")

# Ruta completa a los archivos PKCS#12 usando cadena cruda (r) para evitar problemas de secuencias de escape
ruta_base = "./"

# Ejemplo de uso para cada integrante
integrantes = [
    {"nombre": "AndresSalazar", "archivo_pkcs12": os.path.join(ruta_base, "Salazar.p12"), "contact": "andres@example.com", "location": "Lima", "reason": "Firma de Andre", "password": "salazar123"},
    {"nombre": "JhanAntezana", "archivo_pkcs12": os.path.join(ruta_base, "Antezana.p12"), "contact": "jhan@example.com", "location": "Lima", "reason": "Firma de Jhan", "password": "antezana123"},
    {"nombre": "AngeloVidal", "archivo_pkcs12": os.path.join(ruta_base, "Vidal.p12"), "contact": "angelo@example.com", "location": "Lima", "reason": "Firma de Angelo", "password": "vidal123"},
    {"nombre": "IoriVillegas", "archivo_pkcs12": os.path.join(ruta_base, "Villegas.p12"), "contact": "iori@example.com", "location": "Lima", "reason": "Firma de Iori", "password": "villegas123"},
]

# Verificación del archivo PDF y los archivos .p12
input_pdf = "asistencia.pdf"
if not os.path.exists(input_pdf):
    print(f"El archivo PDF {input_pdf} no existe.")
else:
    for integrante in integrantes:
        pkcs12_path = integrante["archivo_pkcs12"]
        
        if not os.path.exists(pkcs12_path):
            print(f"El archivo {pkcs12_path} no existe.")
        else:
            private_key, certificate, additional_certificates = cargar_certificado(pkcs12_path, integrante['password'])
            if private_key is not None and certificate is not None:
                output_pdf = f"signed_{integrante['nombre']}.pdf"
                firmar_pdf(input_pdf, output_pdf, private_key, certificate, additional_certificates, integrante["contact"], integrante["location"], integrante["reason"])
            else:
                print(f"No se pudo firmar el PDF para {integrante['nombre']}")
