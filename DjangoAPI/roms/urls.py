from django.urls import path
from .views import ROMDelete, ROMCreate, ROMListView, ROMUpdate, ROMDownload, UserRegister, UserViewWishlist, UserAddWishlist, UserDelete, UserListView, UserRemoveWishlist, UserUpdate, RefreshToken, Login, MostPlayed ,ROMDetailView, UserDetailView, ROMSearch, ForgotPassword, ResetPassword, ProtectedRoute, Emuladores, Categorias, EmuladorCreate, EmuladorUpdate, EmuladorDelete, EmuladorDownload, CreateTopico, UpdateTopico, ListTopicos, DeleteTopico
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("roms/", ROMListView.as_view(), name="rom-list"),
    path("roms/detail/", ROMDetailView.as_view(), name="rom-detail"),
    path("roms/search/", ROMSearch.as_view(), name="rom-search"),
    path('roms/mostplayed/', MostPlayed.as_view(), name='rom-mostplayed'),
    path("roms/<str:empresa>/<str:emulador_name>/<str:game_name>/download/", ROMDownload.as_view(), name="rom-download"),
    path("roms/update/", ROMUpdate.as_view(), name="rom-update"),
    path("roms/delete/", ROMDelete.as_view(), name="rom-delete"),
    path("roms/create/", ROMCreate.as_view(), name="rom-create"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/detail/", UserDetailView.as_view(), name="user-detail"),
    path("users/update/", UserUpdate.as_view(), name="user-update"),
    path("users/delete/", UserDelete.as_view(), name="user-delete"),
    path("register/", UserRegister.as_view(), name="user-create"),
    path("users/wishlist/", UserViewWishlist.as_view(), name="user-wishlist"),
    path("users/wishlist/add/", UserAddWishlist.as_view(), name="user-add-wishlist"),
    path("users/wishlist/remove/", UserRemoveWishlist.as_view(), name="user-remove-wishlist"),
    path("token/refresh/", RefreshToken.as_view(), name="token-refresh"),
    path("token/", Login.as_view(), name="token"),
    path("forgot-password/" , ForgotPassword.as_view(), name="forgot-password"),
    path("reset-password/", ResetPassword.as_view(), name="reset-password"),
    path("protected/", ProtectedRoute.as_view(), name="protected"),
    path("emuladores/", Emuladores.as_view(), name="emuladores"),
    path("emulador/create/", EmuladorCreate.as_view(), name="emulador-create"),
    path("emulador/update/", EmuladorUpdate.as_view(), name="emulador-update"),
    path("emulador/delete/", EmuladorDelete.as_view(), name="emulador-delete"),
    path("emulador/<str:emulador_name>/download/", EmuladorDownload.as_view(), name="emulador-download"),
    path("categorias/", Categorias.as_view(), name="categorias")
    path("topicos/create/", CreateTopico.as_view(), name="topico-create"),
    path("topicos/update/", UpdateTopico.as_view(), name="topico-update"),
    path("topicos/list/", ListTopicos.as_view(), name="topico-list"),
    path("topicos/delete/", DeleteTopico.as_view(), name="topico-delete")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)