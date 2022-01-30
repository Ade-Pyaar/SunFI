#inbulit libraries
import json
import requests
from decouple import config

#django imports
from django.contrib.auth import authenticate

#rest_frameworf imports
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status

#import from custom files
from .serializers import SignUpSerializer, LoginSerializer
from .authentication import get_access_token, MyAuthentication
from .models import JWT, Profile



#setting the base url and the authorization header
BASE_URL = "https://the-one-api.dev/v2"
LOGIN = {"Authorization": f"Bearer {config('THE_ONE_API_KEY')}"}


#homepage endpoint
@api_view(['GET'])
def home(request):
    context = {
        'message' : """
        Welcome to my Api

        Here are the list of endpoints, their request type and description

        - GET /characters => should return all characters from the API

        - GET /characters/{id}/quotes => should return all quotes from the specified character

        - POST /signup => allow a user to sign up with their username, email, and password

        - POST /login => allow a user login in and get a token to make authenticated requests

        - POST /characters/{id}/favorites => allows a user favorite a specific character

        - POST /characters/{id}/quotes/{id}/favorites => allows a user favorite a specific quote along with its character information

        - GET /favorites => should return all authenticated user’s favorited items

        """
    }
    return Response(context, status=status.HTTP_200_OK)




#signup endpoint
@api_view(['GET', 'POST'])
def signup(request):
    if request.method == 'GET':
        context = {}
        context['message'] = 'Welcome to User signup page, please pass the required fields'
        context['required'] = 'username, first_name, last_name, password, password_2, email'
        return Response(context, status=status.HTTP_200_OK)

    if request.method == 'POST':
        serializer = SignUpSerializer(data=request.data)
        context = {}
        if serializer.is_valid():
            new_user = serializer.save()

            context['response'] = 'User created successfully, you can now login with your username and password'
            context['username'] = new_user.username
            return Response(context, status=status.HTTP_201_CREATED)

        else:
            context['error'] = serializer.errors
            return Response(context, status=status.HTTP_400_BAD_REQUEST)



# login endpoint
@api_view(["GET", "POST"])
def login(request):
    context = {}
    if request.method == 'GET':
        context['message'] = 'Welcome to login page, please pass the required fields'
        context['required'] = 'username, password'
        return Response(context, status=status.HTTP_200_OK)



    if request.method == "POST":
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user is not None:
                JWT.objects.filter(user_id=user.id).delete()
                access_token = get_access_token({'user_id':user.id})
                JWT.objects.create(user_id=user.id, access=access_token)
                context['message'] = 'Login successful!'
                context['access_token'] = access_token

                return Response(context, status=status.HTTP_200_OK)
            else:
                context['error'] = "Invalid login credentials, please check and try again"
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        else:
            context['error'] = serializer.errors
            return Response(context, status=status.HTTP_400_BAD_REQUEST)




# characters endpoint
@api_view(["GET"])
@authentication_classes((MyAuthentication, ))
@permission_classes((IsAuthenticated, ))
def characters(request):
    context = {"result": []}

    url = BASE_URL + "/character"

    result = requests.get(url, headers=LOGIN)

    result_dict = json.loads(result.text)
    context['result'] = result_dict['docs']


    return Response(context, status=status.HTTP_200_OK)




# characters quotes endpoint
@api_view(["GET"])
@authentication_classes((MyAuthentication, ))
@permission_classes((IsAuthenticated, ))
def characters_quotes(request, xter_id):
    context = {}

    url = BASE_URL + f"/character/{xter_id}/quote"
    result = requests.get(url, headers=LOGIN)

    context['result'] = json.loads(result.text)

    return Response(context, status=status.HTTP_200_OK)




# favorite a character endpoint
@api_view(["POST"])
@authentication_classes((MyAuthentication, ))
@permission_classes((IsAuthenticated, ))
def character_fav(request, xter_id):
    context = {}
    url = BASE_URL + f"/character/{xter_id}"

    single_xter = requests.get(url, headers=LOGIN)
    xter_dict = json.loads(single_xter.text)

    profile = Profile.objects.get(user=request.user)
    profile.fav_xter[xter_id] = {
        'name': xter_dict['docs'][0]['name'],
        'gender': xter_dict['docs'][0]['gender'],
        'race': xter_dict['docs'][0]['race']
    }
    profile.save()

    context['message'] = f"Added user with ID {xter_id} to your favorites successfully."


    return Response(context, status=status.HTTP_200_OK)



# favorite a character's quote endpoin
@api_view(["POST"])
@authentication_classes((MyAuthentication, ))
@permission_classes((IsAuthenticated, ))
def character_quotes_fav(request, xter_id, quote_id):
    context = {}

    url = BASE_URL + f"/character/{xter_id}/quote"

    xter_quotes = requests.get(url, headers=LOGIN)
    quotes_dict = json.loads(xter_quotes.text)
    seen = False

    for quote in quotes_dict['docs']:
        if quote.get('_id', "None") == quote_id:
            profile = Profile.objects.get(user=request.user.id)
            profile.fave_quotes[quote_id] = {
                'quote': quote.get('dialog', "None"),
                'character': {
                    'name': profile.fav_xter[xter_id].get('name', "None"),
                    'race': profile.fav_xter[xter_id].get('race', "None"),
                    'gender': profile.fav_xter[xter_id].get('gender', "None"),
                }
            }
            profile.save()

            context['message'] = f"Added quote with ID {quote_id} to your favorites successfully."

            return Response(context, status=status.HTTP_200_OK)

    if not seen:
        context['error'] = "Quote not found"
        return Response(context, status=status.HTTP_400_BAD_REQUEST)



# get all the favorited items endpoint
@api_view(["GET"])
@authentication_classes((MyAuthentication, ))
@permission_classes((IsAuthenticated, ))
def favourites(request):
    context = {}

    profile = Profile.objects.get(user=request.user.id)

    context['favourite_characters'] = profile.fav_xter
    context['favourite_quotes'] = profile.fave_quotes


    return Response(context, status=status.HTTP_200_OK)