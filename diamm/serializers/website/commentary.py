import ypres


class CommentarySerializer(ypres.Serializer):
    comment = ypres.StrField()
    author = ypres.StrField(attr="author.full_name")
    author_is_staff = ypres.BoolField(attr="author.is_staff")
    created = ypres.StrField()
    comment_type = ypres.IntField()
