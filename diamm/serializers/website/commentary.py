import serpy


class CommentarySerializer(serpy.Serializer):
    comment = serpy.StrField()
    author = serpy.StrField(
        attr="author.full_name"
    )
    created = serpy.StrField()
    comment_type = serpy.IntField()
