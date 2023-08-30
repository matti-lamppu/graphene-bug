# Steps to reproduce the bug

1. Create a virtualenv (`python -m venv venv`)
2. Activate the virtualenv (`source venv/bin/activate` or `venv\Scripts\activate`)
3. Install requirements (`pip install -r requirements.txt`)
4. Run the server (`python manage.py runserver`)
5. Go to graphql endpoint (http://127.0.0.1:8000/graphql/)

# Traceback

```shell
[30/Aug/2023 09:13:35] "GET / HTTP/1.1" 404 2061
Internal Server Error: /graphql/
Traceback (most recent call last):
  File "...\mysite\venv\Lib\site-packages\django\core\handlers\exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\django\core\handlers\base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\django\views\generic\base.py", line 97, in view
    self = cls(**initkwargs)
           ^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\views.py", line 105, in __init__
    schema = graphene_settings.SCHEMA
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\settings.py", line 123, in __getattr__
    val = perform_import(val, attr)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\settings.py", line 62, in perform_import
    return import_from_string(val, setting_name)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\settings.py", line 76, in import_from_string
    module = importlib.import_module(module_path)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\Python311\Lib\importlib\__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "...\mysite\foo\schema.py", line 16, in <module>
    class FooMutation(SerializerMutation):
  File "...\mysite\venv\Lib\site-packages\graphene\types\objecttype.py", line 30, in __new__
    base_cls = super().__new__(
               ^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene\utils\subclass_with_meta.py", line 46, in __init_subclass__
    super_class.__init_subclass_with_meta__(**options)
  File "...\mysite\venv\Lib\site-packages\graphene_django\rest_framework\mutation.py", line 102, in __init_subclass_with_meta__
    output_fields = fields_for_serializer(
                    ^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\rest_framework\mutation.py", line 52, in fields_for_serializer
    fields[name] = convert_serializer_field(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\rest_framework\serializer_converter.py", line 31, in convert_serializer_field
    graphql_type = get_graphene_type_from_serializer_field(field)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\Lib\functools.py", line 909, in wrapper
    return dispatch(args[0].__class__)(*args, **kw)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\rest_framework\serializer_converter.py", line 163, in convert_serializer_field_to_enum
    return convert_choices_to_named_enum_with_descriptions(name, field.choices)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene_django\converter.py", line 101, in convert_choices_to_named_enum_with_descriptions
    return_type = Enum(
                  ^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene\types\enum.py", line 53, in __call__
    return cls.from_enum(
           ^^^^^^^^^^^^^^
  File "...\mysite\venv\Lib\site-packages\graphene\types\enum.py", line 74, in from_enum
    meta_class = type("Meta", (object,), meta_dict)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: EnumType.__call__() takes from 2 to 3 positional arguments but 4 were given
[30/Aug/2023 09:13:39] "GET /graphql/ HTTP/1.1" 500 186631
```

# Issue

The model `foo.models.Foo` has a choice field named `type`. This field is
later exposed to the graphql schema mutations as an enum using `foo.schema.FooSerializer`.
When the `foo.schema.FooMutation` attempts to convert this enum to a graphene enum,
it overrides the globals in `graphene.types.enum.EnumMeta.__new__`
[line 37](https://github.com/graphql-python/graphene/blob/93cb33d359bf2109d1b81eaeaf052cdb06f93f49/graphene/types/enum.py#L37):

```python
globals()[name_] = obj.__enum__
```
Then in `graphene.types.enum.EnumMeta.from_enum`
[line 74](https://github.com/graphql-python/graphene/blob/93cb33d359bf2109d1b81eaeaf052cdb06f93f49/graphene/types/enum.py#L74):

```python
meta_class = type("Meta", (object,), meta_dict)
```
Attempting to use the `type` function to construct a new Meta class here
fails because `type` has been overridden in the globals. `type` now calls
`obj.__enum__`, which is not intended and results in the error above.

# Possible solution

Do `import builtins` and then use `builtins.type` instead of `type`?
