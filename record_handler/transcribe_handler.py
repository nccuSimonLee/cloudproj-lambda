import requests
import uuid
from custom_waiter import CustomWaiter, WaitState



class TranscribeCompleteWaiter(CustomWaiter):
    """
    Waits for the transcription to complete.
    """
    def __init__(self, client):
        super().__init__(
            'TranscribeComplete', 'GetTranscriptionJob',
            'TranscriptionJob.TranscriptionJobStatus',
            {'COMPLETED': WaitState.SUCCESS, 'FAILED': WaitState.FAILURE},
            client, delay=3)

    def wait(self, job_name):
        self._wait(TranscriptionJobName=job_name)


class TranscribeHandler:
    def __init__(self, transcribe):
        self.transcribe = transcribe
        self.waiter = TranscribeCompleteWaiter(transcribe)
    
    def record_to_texts(self, bucket_name, key):
        job = self._start_transcription_job(bucket_name, key)
        job_name = job['TranscriptionJobName']
        results = self._request_transcribe_results(job_name)
        texts = ''.join(line['transcript'] for line in results['transcripts'])
        return texts

    def _start_transcription_job(self, bucket_name, key):
        job_name = uuid.uuid4().hex
        job_uri = f's3://{bucket_name}/{key}'
        response = self.transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': job_uri},
            MediaFormat='wav',
            LanguageCode='zh-CN'
        )
        job = response['TranscriptionJob']
        return job

    def _request_transcribe_results(self, job_name):
        self.waiter.wait(job_name)
        job = self._get_transcription_job(job_name)
        response = requests.get(job['Transcript']['TranscriptFileUri'])
        self.transcribe.delete_transcription_job(TranscriptionJobName=job_name)
        return response.json()['results']
    
    def _get_transcription_job(self, job_name):
        response = self.transcribe.get_transcription_job(
            TranscriptionJobName=job_name
        )
        job = response['TranscriptionJob']
        return job
