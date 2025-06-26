# movies/mcp_views.py 파일 생성 (필요시)

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View


# 검색 결과 [5] 패턴: CSRF 예외 데코레이터
@method_decorator(csrf_exempt, name='dispatch')
class MCPView(View):
    """MCP 엔드포인트 CSRF 예외 처리"""

    def get(self, request):
        return JsonResponse({
            'name': 'movie-personality-mcp',
            'version': '1.0.0',
            'status': 'running'
        })

    def post(self, request):
        return JsonResponse({
            'success': True,
            'message': 'MCP server is ready'
        })
