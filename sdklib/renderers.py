from urllib import quote_plus

from urllib3.filepost import encode_multipart_formdata
from urllib3.fields import RequestField, guess_content_type

from .util.file import guess_filename_stream
from .util.structures import to_key_val_list, to_key_val_dict
from .compat import urlencode


class MultiPartRender(object):

    def __init__(self, boundary="----------ThIs_Is_tHe_bouNdaRY_$"):
        self.boundary = boundary

    def encode_params(self, data=None, files=None, **kwargs):
        """
        Build the body for a multipart/form-data request.
        Will successfully encode files when passed as a dict or a list of
        tuples. Order is retained if data is a list of tuples but arbitrary
        if parameters are supplied as a dict.
        The tuples may be string (filepath), 2-tuples (filename, fileobj), 3-tuples (filename, fileobj, contentype)
        or 4-tuples (filename, fileobj, contentype, custom_headers).
        """
        if isinstance(data, basestring):
            raise ValueError("Data must not be a string.")

        # optional args
        boundary = kwargs.get("boundary", None)

        new_fields = []
        fields = to_key_val_list(data or {})
        files = to_key_val_list(files or {})

        for field, val in fields:
            if isinstance(val, basestring) or not hasattr(val, '__iter__'):
                val = [val]
            for v in val:
                if v is not None:
                    # Don't call str() on bytestrings: in Py3 it all goes wrong.
                    if not isinstance(v, bytes):
                        v = str(v)

                    new_fields.append(
                        (field.decode('utf-8') if isinstance(field, bytes) else field,
                         v.encode('utf-8') if isinstance(v, str) else v))

        for (k, v) in files:
            # support for explicit filename
            ft = None
            fh = None
            if isinstance(v, (tuple, list)):
                if len(v) == 2:
                    fn, fp = v
                elif len(v) == 3:
                    fn, fp, ft = v
                else:
                    fn, fp, ft, fh = v
            else:
                fn, fp = guess_filename_stream(v)
                ft = guess_content_type(fn)

            if isinstance(fp, (str, bytes, bytearray)):
                fdata = fp
            else:
                fdata = fp.read()

            rf = RequestField(name=k, data=fdata, filename=fn, headers=fh)
            rf.make_multipart(content_type=ft)
            new_fields.append(rf)

        if boundary is None:
            boundary = self.boundary
        body, content_type = encode_multipart_formdata(new_fields, boundary=boundary)

        return body, content_type


class FormRender(object):

    VALID_COLLECTION_FORMATS = ['multi', 'csv', 'ssv', 'tsv', 'pipes', 'encoded']
    COLLECTION_SEPARATORS = {"csv": ",", "ssv": " ", "tsv": "\t", "pipes": "|"}

    def __init__(self, collection_format='multi'):
        self.content_type = 'application/x-www-form-urlencoded'
        self.collection_format = collection_format

    @property
    def collection_format(self):
        return self._collection_format

    @collection_format.setter
    def collection_format(self, value):
        assert value in self.VALID_COLLECTION_FORMATS

        self._collection_format = value

    def encode_params(self, data=None, **kwargs):
        """Encode parameters in a piece of data.
        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """
        collection_format = kwargs.get("collection_format", self.collection_format)

        if data is None:
            return "", self.content_type
        elif isinstance(data, (str, bytes)):
            return data, self.content_type
        elif hasattr(data, 'read'):
            return data, self.content_type
        elif collection_format == 'multi' and hasattr(data, '__iter__'):
            result = []
            for k, vs in to_key_val_list(data):
                if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (k.encode('utf-8') if isinstance(k, str) else k,
                             v.encode('utf-8') if isinstance(v, str) else v))
            return urlencode(result, doseq=True), self.content_type
        elif collection_format == 'encoded' and hasattr(data, '__iter__'):
            return urlencode(data, doseq=False), self.content_type
        elif hasattr(data, '__iter__'):
            results = []
            for k, vs in to_key_val_dict(data).items():
                if isinstance(vs, list):
                    v = self.COLLECTION_SEPARATORS[collection_format].join(quote_plus(e) for e in vs)
                    key = k + '[]'
                else:
                    v = quote_plus(vs)
                    key = k
                results.append("%s=%s" % (key, v))

            return '&'.join(results), self.content_type
        else:
            return data, self.content_type


class PlainTextRender(object):

    def __init__(self, doseq=True):
        self.content_type = 'text/plain'

    def encode_params(self, data=None, **kwargs):
        """Encode parameters in a piece of data.
        Will successfully encode parameters when passed as a dict or a list of
        2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
        if parameters are supplied as a dict.
        """
        if data is None:
            return "", self.content_type
        elif isinstance(data, (str, bytes)):
            return data, self.content_type
        elif hasattr(data, 'read'):
            return data, self.content_type
        elif hasattr(data, '__iter__'):
            result = []
            for k, vs in to_key_val_list(data):
                if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                    vs = [vs]
                for v in vs:
                    if v is not None:
                        result.append(
                            (k.encode('utf-8') if isinstance(k, str) else k,
                             v.encode('utf-8') if isinstance(v, str) else v))
            return urlencode(result, doseq=self.doseq), self.content_type
        else:
            return data, self.content_type


class JSONRender(object):

    def __init__(self, boundary="----------ThIs_Is_tHe_bouNdaRY_$"):
        self.boundary = boundary

    def encode_params(self, data=None, files=None, **kwargs):
        """
        Build the body for a multipart/form-data request.
        Will successfully encode files when passed as a dict or a list of
        tuples. Order is retained if data is a list of tuples but arbitrary
        if parameters are supplied as a dict.
        The tuples may be string (filepath), 2-tuples (filename, fileobj), 3-tuples (filename, fileobj, contentype)
        or 4-tuples (filename, fileobj, contentype, custom_headers).
        """
        if isinstance(data, basestring):
            raise ValueError("Data must not be a string.")

        # optional args
        boundary = kwargs.get("boundary", None)

        new_fields = []
        fields = to_key_val_list(data or {})
        files = to_key_val_list(files or {})

        for field, val in fields:
            if isinstance(val, basestring) or not hasattr(val, '__iter__'):
                val = [val]
            for v in val:
                if v is not None:
                    # Don't call str() on bytestrings: in Py3 it all goes wrong.
                    if not isinstance(v, bytes):
                        v = str(v)

                    new_fields.append(
                        (field.decode('utf-8') if isinstance(field, bytes) else field,
                         v.encode('utf-8') if isinstance(v, str) else v))

        for (k, v) in files:
            # support for explicit filename
            ft = None
            fh = None
            if isinstance(v, (tuple, list)):
                if len(v) == 2:
                    fn, fp = v
                elif len(v) == 3:
                    fn, fp, ft = v
                else:
                    fn, fp, ft, fh = v
            else:
                fn, fp = guess_filename_stream(v)
                ft = guess_content_type(fn)

            if isinstance(fp, (str, bytes, bytearray)):
                fdata = fp
            else:
                fdata = fp.read()

            rf = RequestField(name=k, data=fdata, filename=fn, headers=fh)
            rf.make_multipart(content_type=ft)
            new_fields.append(rf)

        if boundary is None:
            boundary = self.boundary
        body, content_type = encode_multipart_formdata(new_fields, boundary=boundary)

        return body, content_type