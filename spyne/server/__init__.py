from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from spyne.server.django import DjangoApplication
from spyne.server.django import class StreamingDjangoApplication
from spyne.server.django import class DjangoServer
from spyne.server.django import class DjangoView
