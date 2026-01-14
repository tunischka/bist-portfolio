"""
Version ve deployment bilgisi
"""
import subprocess
from datetime import datetime


def get_git_info():
    """Git commit hash ve tarih bilgisini al"""
    try:
        # Commit hash (kısa)
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode('ascii').strip()
        
        # Commit tarihi
        commit_date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=short'],
            stderr=subprocess.DEVNULL
        ).decode('ascii').strip()
        
        return {
            'hash': commit_hash,
            'date': commit_date,
            'version': f"v{commit_date}-{commit_hash}"
        }
    except:
        # Git yok veya hata
        return {
            'hash': 'unknown',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'version': 'dev'
        }


def get_version_string():
    """Versiyon string'i döndür"""
    info = get_git_info()
    return info['version']
