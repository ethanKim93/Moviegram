  #csrf 예외를 위해 import
from django.views.decorators.csrf import csrf_exempt
from movies.models import Movie
# JSON 타입 반환을 위해 import
from django.http import JsonResponse, response
import json
import random

#정보를 저장하는 context입니다.


@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        req = json.loads(request.body)

        #request의 action을 파악합니다.
        action = req.get('queryResult').get('action')
        
        #params를 획득합니다.
        params = req.get('queryResult').get('parameters')

        # action에 따라서 이동합니다.
        if action == 'recommendation_create':
            return recommendation_create(params)
  
          

def recommendation_create(request, params):
    
  
    movies = Movie.objects.all()
    item = random.choice(movies)

    item.save()
    
    
    response = {
       
    "fulfillmentMessages": [
            {
             "fulfillmentText":  '추천영화 {}는 어떠세요?'.format(item.title),
            }
        ],
      "outputContexts": [
    {
        "name": "projects/newagent-vdhg/agent/sessions/b262b96f-8a00-4cd5-3c09-0ddf0584b2e9/contexts/recommendation_create-followup",
        "lifespanCount": 2,
        "parameters": {
        "followrecommendation": "추천",
      }
    }
    ],
    
    "session": "projects/newagent-vdhg/agent/sessions/b262b96f-8a00-4cd5-3c09-0ddf0584b2e9" 
    }
    return JsonResponse(response, safe=False)

# def recommendation_create(request, params):
    
#     recommendation = params.get('followrecommendation')
#     movies = Movie.objects.all()
#     item = random.choice(movies)

#     item.save()
    
    
#     response = {
       
#      "fulfillmentText":  '추천영화 {}는 어떠세요?'.format(item.title),
#       "outputContexts": [
#                     {
#                       "name": recommendation,
#                       "lifespanCount": 2,
#                       "parameters": {
#                         "followrecommendation": item.id
#                       }
#                     }
#                   ]
#     }
#     return JsonResponse(response, safe=False)