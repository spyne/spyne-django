# encoding: utf-8
#
# This file is part of the spyne-django project.
# Copyright (c) spyne-django contributors, All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the {organization} nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#



"""The Django client transport for testing Spyne apps the way you'd test Django
apps."""


from __future__ import absolute_import

from django.test.client import Client

from spyne.client import Service
from spyne.client import ClientBase
from spyne.client import RemoteProcedureBase


class _RemoteProcedure(RemoteProcedureBase):
    def __call__(self, *args, **kwargs):
        response = self.get_django_response(*args, **kwargs)
        code = response.status_code
        self.ctx.in_string = [response.content]

        # this sets ctx.in_error if there's an error, and ctx.in_object if
        # there's none.
        self.get_in_object(self.ctx)

        if not (self.ctx.in_error is None):
            raise self.ctx.in_error
        elif code >= 400:
            raise self.ctx.in_error
        else:
            return self.ctx.in_object

    def get_django_response(self, *args, **kwargs):
        """Return Django ``HttpResponse`` object as RPC result."""
        # there's no point in having a client making the same request more than
        # once, so if there's more than just one context, it is a bug.
        # the comma-in-assignment trick is a general way of getting the first
        # and the only variable from an iterable. so if there's more than one
        # element in the iterable, it'll fail miserably.
        self.ctx, = self.contexts

        # sets ctx.out_object
        self.get_out_object(self.ctx, args, kwargs)

        # sets ctx.out_string
        self.get_out_string(self.ctx)

        out_string = ''.join(self.ctx.out_string)
        # Hack
        client = Client()
        return client.post(self.url, content_type='text/xml', data=out_string)


class DjangoTestClient(ClientBase):
    """The Django test client transport."""

    def __init__(self, url, app):
        super(DjangoTestClient, self).__init__(url, app)

        self.service = Service(_RemoteProcedure, url, app)
