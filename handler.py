import os
import io
import time
import urllib.parse
from datetime import datetime
from decimal import Decimal
import boto3
from PIL import Image

#Inizializzazione
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def process_image(event, context):
    start_time = time.time()
    
    try:
        #Estrazione evento S3
        record = event['Records'][0]
        src_bucket = record['s3']['bucket']['name']
        src_key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        
        print(f"Inizio elaborazione per: {src_key} dal bucket: {src_bucket}")
        
        #Download dell'immagine
        response = s3_client.get_object(Bucket=src_bucket, Key=src_key)
        input_bytes = response['Body'].read()
        original_size = len(input_bytes)
        
        #Elaborazione
        processing_start_time = time.time()
        with Image.open(io.BytesIO(input_bytes)) as img:
            #Conversione in RGB
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            #Ridimensionamento proporzionale
            max_width = 1024
            if img.width > max_width:
                aspect_ratio = img.height / img.width
                new_height = int(max_width * aspect_ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            #Salvataggio nel buffer di output compresso
            output_buffer = io.BytesIO()
            img.save(output_buffer, format="JPEG", quality=80, optimize=True)
            output_bytes = output_buffer.getvalue()
        
        processing_duration_ms = int((time.time() - processing_start_time) * 1000)
        processed_size = len(output_bytes)
        
        #Upload dell'immagine ottimizzata nel bucket
        dest_bucket = os.environ['OUTPUT_BUCKET']
        base_name = os.path.splitext(src_key)[0]
        dest_key = f"optimized-{base_name}.jpg"
        
        s3_client.put_object(
            Bucket=dest_bucket,
            Key=dest_key,
            Body=output_bytes,
            ContentType="image/jpeg"
        )
        
        #Calcolo metriche
        total_duration_ms = int((time.time() - start_time) * 1000)
        compression_ratio = round(((original_size - processed_size) / original_size) * 100, 2)
        
        #Registrazione su DynamoDB
        table = dynamodb.Table(os.environ['TABLE_NAME'])
        metric_item = {
            'imageId': f"{int(time.time() * 1000)}_{src_key}",
            'originalFilename': src_key,
            'processedFilename': dest_key,
            'originalSizeKB': str(round(original_size / 1024, 2)),
            'processedSizeKB': str(round(processed_size / 1024, 2)),
            'compressionRatioPercent': Decimal(str(compression_ratio)),
            'processingTimeMs': processing_duration_ms,
            'totalExecutionTimeMs': total_duration_ms,
            'timestamp': datetime.utcnow().isoformat() + "Z"
        }
        table.put_item(Item=metric_item)
        
        print(f"Elaborazione completata in {total_duration_ms}ms: {metric_item}")
        
        return {
            'statusCode': 200,
            'body': 'Image processed successfully'
        }
        
    except Exception as e:
        print(f"Errore durante l'elaborazione dell'immagine: {str(e)}")
        raise e