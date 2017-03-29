import serpy


class CommentarySerializer(serpy.Serializer):
    comment = serpy.StrField()
    author = serpy.StrField(
        attr="author.full_name"
    )
    author_is_staff = serpy.BoolField(
        attr="author.is_staff"
    )
    created = serpy.StrField()
    comment_type = serpy.IntField()
