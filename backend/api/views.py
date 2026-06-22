import io
import uuid
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ml_utils import predict_tyre_batch
from .serializers import UploadCSVSerializer, BatchRequestSerializer

# In-memory session storage (for demo only)
SESSION_DATA = {}
BATCH_SIZE = 6

class UploadView(APIView):
    def post(self, request):
        serializer = UploadCSVSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            df = pd.read_csv(file)
            session_id = str(uuid.uuid4())
            # Split into batches
            batches = [df.iloc[i:i+BATCH_SIZE] for i in range(0, len(df), BATCH_SIZE)]
            SESSION_DATA[session_id] = batches
            return Response({
                'session_id': session_id,
                'batch_count': len(batches)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BatchView(APIView):
    def get(self, request):
        session_id = request.query_params.get('session_id')
        batch_num = int(request.query_params.get('batch', 0))
        batches = SESSION_DATA.get(session_id)
        if not batches or batch_num >= len(batches):
            return Response({'error': 'Invalid session or batch'}, status=404)
        batch_df = batches[batch_num]
        predictions = predict_tyre_batch(batch_df)
        return Response({'batch': batch_num, 'data': predictions})
