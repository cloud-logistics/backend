#! /usr/bin/env python
# -*- coding: utf-8 -*-

from rest_framework import views
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
import os
from rentservice.utils import logger
from rentservice.utils.retcode import retcode, errcode
import uuid
from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config
import base64

log = logger.get_logger(__name__)


class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)
    access_key = 'WlfLj84tEqH7_FX-GhAnj30OmhreeeUYtBYgwnCN'
    secret_key = 'O8efy3dIot_jv-xyh7kC_QBZ_2bUca5C4bdH7PXj'
    bucket_name = 'cloudbox'
    base_url = 'oyzmceglk.bkt.clouddn.com'

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        ret = {'status': False, 'data': None, 'error': None}
        f = open(os.path.join('.', file_obj.name), 'wb')
        try:
            if file_obj.multiple_chunks():
                for chunk in file_obj.chunks():
                    f.write(chunk)
            else:
                f.write(file_obj.read())
        except Exception, e:
            log.error(repr(e))
            ret['error'] = e
        finally:
            f.close()
            ret['status'] = True
        try:
            tmpfile_path = os.path.join('.', file_obj.name)
            if os.path.exists(tmpfile_path):
                q = Auth(self.access_key, self.secret_key)
                log.info("begin base64 filename")
                file_name_base64 = base64.b64encode(self.to_str(file_obj.name))
                log.info("filename=%s, filenametype=%s, base64filename=%s" % (file_obj.name, type(file_obj.name),
                                                                              file_name_base64))
                key = "%s-%s" % (uuid.uuid1(), file_name_base64)
                token = q.upload_token(self.bucket_name, key, 3600)
                ret, info = put_file(token, key, tmpfile_path)
                if info.status_code == 200:
                    ret['url'] = "%s/%s" % (self.base_url, key)
                else:
                    ret['url'] = ""
                os.remove(tmpfile_path)
        except Exception, e:
            log.error(repr(e))
            ret['error'] = e
            os.remove(tmpfile_path)
            return Response(data=errcode('0500', ret), status=500)
        return Response(data=retcode(ret, "0000", "Succ"), status=200)

    def to_str(self, str_or_unicode):
        if isinstance(str_or_unicode, unicode):
            value = str_or_unicode.encode('utf-8')
        else:
            value = str_or_unicode
        return value
