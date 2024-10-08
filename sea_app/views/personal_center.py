from functools import reduce

from django.contrib import auth
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponseRedirect

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
import datetime
from sea import settings

from sdk.shopify import shopify_oauth_info
from sea_app import models
from sea_app.serializers import personal_center, store
from sea_app.utils.menu_tree import MenuTree
from sea_app.pageNumber.pageNumber import PNPagination
from sea_app.filters import personal_center as personal_center_filters
from sea_app.permission.permission import UserPermission
from sdk.shopify.shopify_oauth_info import ShopifyBase
from sdk.shopify.get_shopify_products import ProductsApi
from sdk.pinterest import pinterest_api
from sea_app.views import reports
from sea_app.utils import random_code
from task.task_processor import TaskProcessor


class LoginView(generics.CreateAPIView):
    """登陆"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username', '')
            password = request.data.get('password', '')
            code = request.data.get("code", "")
            if code:
                print(username,code)
                obj = models.User.objects.filter(username=username,code=code).first()
                print(obj)
            else:
                obj = models.User.objects.filter(username=username).first()
            if obj and obj.is_active == 0:
                if code:
                    print(obj.code,code)
                    if obj.code == code:
                        obj.is_active = 1
                        obj.save()
                    else:
                        return Response({"detail": "The account is not activated, Please check the last email。"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"detail": "The account is not activated"}, status=status.HTTP_400_BAD_REQUEST)
            user = auth.authenticate(username=username, password=password)
            if not user:
                return Response({"detail": "User name password error"}, status=status.HTTP_400_BAD_REQUEST)
            if user:
                res = {}
                res["user"] = personal_center.LoginSerializer(instance=user, many=False).data
                store_instance = models.Store.objects.filter(user_id=user.id).first()
                # res["store"] = store.StoreSerializer(instance=store_instance, many=False).data
                payload = jwt_payload_handler(user)
                res["token"] = "{} {}".format(settings.JWT_AUTH_HEADER_PREFIX, jwt_encode_handler(payload))
                return Response(res, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    """注册"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.RegisterSerializer


class SetPasswordView(generics.UpdateAPIView):
    """注册状态设置密码"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.SetPasswordSerializer


class SetPasswordsView(generics.UpdateAPIView):
    """登陆状态设置密码"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.SetPasswordsSerializer
    permission_classes = (IsAuthenticated, UserPermission)
    authentication_classes = (JSONWebTokenAuthentication,)


# class UserView(generics.ListCreateAPIView):
#     """用户 增 列表展示"""
#     queryset = models.User.objects.all()
#     serializer_class = personal_center.UserSerializer
#     pagination_class = PNPagination
#     filter_backends = (personal_center_filters.UserFilter, DjangoFilterBackend)
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (JSONWebTokenAuthentication,)
#     filterset_fields = ("nickname",)


class UserOperView(generics.RetrieveUpdateAPIView):
    """用户 删 该 查"""
    queryset = models.User.objects.all()
    serializer_class = personal_center.UserOperSerializer
    permission_classes = (IsAuthenticated, UserPermission)
    authentication_classes = (JSONWebTokenAuthentication,)


# class RoleView(generics.ListCreateAPIView):
#     """角色 增 列表展示"""
#     queryset = models.Role.objects.all()
#     serializer_class = personal_center.RoleSerializer
#     pagination_class = PNPagination
#     filter_backends = (personal_center_filters.RoleFilter,)
#     permission_classes = (IsAuthenticated,)
#     authentication_classes = (JSONWebTokenAuthentication,)
#
#     def list(self, request, *args, **kwargs):
#         show_more = request.query_params.get("show_more", None)
#         if not show_more:
#             return super(RoleView, self).list(request)
#         queryset = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


# class RoleOperView(generics.RetrieveUpdateDestroyAPIView):
#     """角色 删 改 查"""
#     queryset = models.Role.objects.all()
#     serializer_class = personal_center.RoleSerializer
#     permission_classes = (IsAuthenticated, RolePermission)
#     authentication_classes = (JSONWebTokenAuthentication,)
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         is_exit = models.User.objects.filter(role=instance)
#         if is_exit:
#             return Response({"detail": "The role also has user binding"}, status=status.HTTP_400_BAD_REQUEST)
#         self.perform_destroy(instance)
#         return Response(status=status.HTTP_204_NO_CONTENT)


class StoreAuthView(APIView):
    """店铺授权接口"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        instance = models.Store.objects.filter(id=kwargs["pk"]).first()
        # if instance.authorized == 1:
        #     return Response({"detail": "This store is authorized"}, status=status.HTTP_400_BAD_REQUEST)
        url = ShopifyBase("ordersea.myshopify.com").ask_permission("d")
        return Response({"message": url})


class PinterestAccountAuthView(APIView):
    """账户授权"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # instance = models.PinterestAccount.objects.filter(id=kwargs["pk"]).first()
        # if not instance:
        #     return Response({"detail": "The resource was not found"}, status=status.HTTP_400_BAD_REQUEST)
        # if instance.authorized == 1:
        #     return Response({"detail": "This account is authorized"}, status=status.HTTP_400_BAD_REQUEST)
        # state = "%s|%d" % (instance.account, request.user.id)
        url = pinterest_api.PinterestApi().get_pinterest_url(state=request.user.id)
        return Response({"message": url})


class PinterestAccountCancelAuthView(generics.UpdateAPIView):
    """账号取消授权"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = personal_center.CancelAuthSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def put(self, request, *args, **kwargs):
        account_id = kwargs.get('pk', '')
        # 需要先将account关联的rule进行取消
        models.Rule.objects.filter(pinterest_account_id=account_id, state__in=[-1,0,1,2]).update(state=5)
        # 需要将account关联的publish record进行取消
        models.PublishRecord.objects.filter(pinterest_account_id=account_id, state__in=[0,1,2]).update(state=5)
        return self.update(request, *args, **kwargs)


class ShopifyCallback(APIView):
    """shopify 回调接口"""
    def get(self, request):
        code = request.query_params.get("code", None)
        shop = request.query_params.get("shop", None)
        if not code or not shop:
            return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        shop_name = shop.split(".")[0]
        result = ShopifyBase(shop).get_token(code)
        if result["code"] != 1:
            return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        instance = models.Store.objects.filter(uri=shop).first()
        if instance:
            instance.token = result["data"]
            instance.save()
            user_instance = models.User.objects.filter(id=instance.user_id).first()
            # user_instance.is_active = 0
            # user_instance.password = ""
            user_instance.save()
            email = user_instance.email
        else:
            store_data = {"name": shop_name, "url": shop, "uri": shop, "token": result["data"], "platform": models.Platform.objects.filter(id=1).first()}
            instance = models.Store.objects.create(**store_data)
            info = ProductsApi(access_token=result["data"], shop_uri=shop).get_shop_info()
            email = info["data"]["shop"]["email"]
            user_data = {"username": shop, "email": email, "is_active": 0, "code": random_code.create_random_code(6, True)}
            user_instance = models.User.objects.create(**user_data)
            instance.user = user_instance
            instance.email = email
            instance.save()
        return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/shopfy_regist?shop={}&email={}&id={}".format(shop, email, user_instance.id))


class PinterestCallback(APIView):
    """pinterest 回调接口"""

    def get(self, request, *args, **kwargs):
        code = request.query_params.get("code", None)
        uid = request.query_params.get("state", None)
        if not code or not uid:
            return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        uid = int(uid)
        result = pinterest_api.PinterestApi().get_token(code)
        if result["code"] != 1:
            return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        # 判断token是否为当前用户的token
        token = result["data"].get("access_token", "")
        print("current token：{}".format(token))
        if token:
            result = pinterest_api.PinterestApi(access_token=token).get_user_info()
            if result["code"] != 1:
                return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
            account_info = result.get("data", {})
            if not account_info:
                return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
            uuid = account_info.get("id", '')
            nickname = account_info.get("username", "")
            # description = account_info.get("bio", "")
            # account_type = account_info.get("account_type", "")
            # type = 0 if account_type == "individual" else 1
            # create_time = account_info.get("created_at", "")
            # if create_time:
            #     create_at = datetime.datetime.strptime(create_time, "%Y-%m-%dT%H:%M:%S")
            # counts = account_info.get("counts", {})
            # pins = counts.get("pins", 0)
            # boards = counts.get("boards", 0)
            # followings = counts.get("following")
            # followers = counts.get("followers")
            is_uuid = models.PinterestAccount.objects.filter(**{"uuid":uuid,"user_id":uid}).first()
            if is_uuid:
                return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=3")
            pin_account = models.PinterestAccount.objects.create(**{"user_id":uid, "account": nickname, "nickname": nickname, "uuid": uuid,"token":token,"authorized":1})
            # print("-----update pinterest id=", pin_account.id)
            # TaskProcessor().update_pinterest_data(pin_account.id)
        else:
            return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=1")
    # def get(self, request, *args, **kwargs):
        # code = request.query_params.get("code", None)
        # state = request.query_params.get("state", None)
        # account_uri = state.split("|")[0]
        # uid = state.split("|")[1]
        # if not code or not account_uri:
        #     return Response({"message": "auth faild"})
        # result = pinterest_api.PinterestApi().get_token(code)
        # if result["code"] != 1:
        #     return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        # # 判断token是否为当前用户的token
        # token = result["data"].get("access_token", "")
        # print("current token：{}".format(token))
        # # user_info = pinterest_api.PinterestApi(access_token=token).get_user_info()
        # # print("current user info: {}".format(user_info))
        # # if user_info["code"] == 1:
        # #     if user_info["data"].get("url").lower() == account_uri.lower():
        # #         models.PinterestAccount.objects.filter(account=account_uri).update(
        # #             token=token, authorized=1)
        # #         return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=1")
        #
        # if token:
        #     result = pinterest_api.PinterestApi(access_token=token).get_user_info()
        #     if result["code"] != 1:
        #         return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        #     account_info = result.get("data", {})
        #     if not account_info:
        #         return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        #     account_uuid = account_info.get("id", '')
        #     is_uuid = models.PinterestAccount.objects.filter(uuid=int(account_uuid)).first()
        #     if is_uuid:
        #         return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=3")
        #     pin_account = models.PinterestAccount.objects.filter(account=account_uri)
        #     if pin_account:
        #         pin_account.update(token=token, authorized=1)
        #         pin_account_id = pin_account.first().id
        #         print("-----update pinterest id=", pin_account_id)
        #         TaskProcessor().update_pinterest_data(pin_account_id)
        #     else:
        #         return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        # else:
        #     return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=2")
        # return HttpResponseRedirect(redirect_to="https://pinbooster.seamarketings.com/aut_state?state=1")


class OperationRecord(generics.ListAPIView):
    """操作记录 视图"""
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        data = reports.operation_record(request)
        return Response(data)


class ShopifyAuthView(APIView):
    """shopify 授权页面"""
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (JSONWebTokenAuthentication,)

    def get(self, request, *args, **kwargs):
        # 获取get请求的参数
        shop_uri = request.query_params.get("shop", None)
        if not shop_uri:
            return Response({"message": "no shop"})
        # shop_uri = shop_name + ".myshopify.com"
        permission_url = shopify_oauth_info.ShopifyBase(shop_uri).ask_permission(shop_uri)
        return HttpResponseRedirect(redirect_to=permission_url)


class PostTimeView(generics.ListCreateAPIView):
    """发布时间节点"""
    queryset = models.PinterestAccount.objects.all()
    serializer_class = personal_center.PostTimeSerializer
    filter_backends = (personal_center_filters.PostTimeFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def post(self, request, *args, **kwargs):
        data = request.data
        instance = self.queryset.get(pk=data.get("account_id", None))
        post_time = data.get("post_time", None)
        if post_time:
            # 在此计算post_time的every
            post_time = eval(post_time)
            post_time.pop("every")
            post_time["every"] = {"state": 1,
                                   "time": self.intersection_for_multi_list([lambda x: x["time"] if x["state"] == 1 else [], post_time.values()])}
            instance.post_time = str(post_time).replace("'", '"')
            instance.save()
            return Response({"message": "update account {} post_time success.".format(instance.nickname)}, status=status.HTTP_201_CREATED)
        return Response({"message": "no post_time."}, status=status.HTTP_400_BAD_REQUEST)

    def intersection_for_multi_list(self, item_list):
        fm = lambda x, y: list(set(x).intersection(set(y))) if isinstance(x, list) and isinstance(y, list) else 'error'
        fn = lambda x: x[0] if len(x) == 1 else [] if len(x) == 0 else reduce(fm, tuple(y for y in x))
        item_list = fn(item_list)
        return sorted(item_list)


class SelectPostTimeView(generics.ListAPIView):
    queryset = models.PinterestAccount.objects.all()
    filter_backends = (personal_center_filters.SelectPostTimeFilter,)
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            return Response({"message": "PinterestAccount matching query does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(queryset)
