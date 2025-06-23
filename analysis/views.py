from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from .models import PersonalityAnalysis
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_personality(request):
    """성격 분석 실행 함수"""
    try:
        print(f"🧠 성격 분석 시작 - 사용자: {request.user}")

        # 임시 분석 결과 (실제 분석 로직으로 교체 필요)
        response_data = {
            'success': True,
            'message': '8편의 영화를 분석하여 성격 특성을 도출했습니다.',
            'confidence': 0.5559168108424153,
            'data': {
                'personality': {
                    'openness': 0.6713333333333333,
                    'conscientiousness': 0.5976666666666668,
                    'extraversion': 0.7200000000000001,
                    'agreeableness': 0.6586666666666667,
                    'neuroticism': 0.4326666666666667,
                    'movies_analyzed': 8,
                    'personality_summary': '창의적이고 사회적인 성격'
                }
            }
        }

        print(f"✅ 분석 완료: {response_data}")
        return Response(response_data, status=201)

    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return Response({
            'error': f'분석 중 오류가 발생했습니다: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_latest_analysis(request):
    """최신 분석 결과 조회 함수"""
    try:
        print(f"🔍 분석 결과 조회 - 사용자: {request.user}")

        # PersonalityAnalysis 모델에서 데이터 조회
        analyses = PersonalityAnalysis.objects.all().order_by('-created_at')

        if analyses.exists():
            analysis = analyses.first()
            print(f"✅ 분석 발견: 신뢰도 {analysis.confidence_score}")

            response_data = {
                'success': True,
                'confidence': analysis.confidence_score,
                'message': f"8편의 영화를 분석하여 도출된 결과입니다.",
                'data': {
                    'personality': {
                        'openness': analysis.openness,
                        'conscientiousness': analysis.conscientiousness,
                        'extraversion': analysis.extraversion,
                        'agreeableness': analysis.agreeableness,
                        'neuroticism': analysis.neuroticism,
                        'movies_analyzed': 8,
                        'personality_summary': '성격 분석 완료',
                    },
                    'values': {
                        'creativity_innovation': 0.75,
                        'social_connection': 0.68,
                        'achievement_success': 0.58,
                        'harmony_stability': 0.41,
                        'authenticity_depth': 0.52
                    }
                }
            }

            print(f"📤 응답 데이터: 신뢰도 {response_data['confidence']}")
            return Response(response_data)
        else:
            print("❌ 분석 결과 없음")
            return Response({
                'error': '분석 결과가 없습니다.'
            }, status=404)

    except Exception as e:
        print(f"❌ 조회 실패: {e}")
        return Response({
            'error': f'결과 조회 중 오류: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_analysis_statistics(request):
    """분석 통계 조회 함수"""
    try:
        print(f"📊 통계 조회 - 사용자: {request.user}")

        # 영화 평가 수 확인
        from movies.models import UserMoviePreference
        user_preferences = UserMoviePreference.objects.filter(user=request.user)
        total_movies_rated = user_preferences.count()

        response_data = {
            'success': True,
            'total_movies_rated': total_movies_rated,
            'analysis_ready': total_movies_rated >= 5,
            'min_movies_required': 5
        }

        print(f"📊 통계 응답: {response_data}")
        return Response(response_data)

    except Exception as e:
        print(f"❌ 통계 조회 실패: {e}")
        return Response({'error': str(e)}, status=500)
