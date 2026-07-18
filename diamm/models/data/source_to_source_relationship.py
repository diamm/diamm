from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


class SourceToSourceRelationship(models.Model):
    class Meta:
        app_label = "diamm_data"
        constraints = [
            models.CheckConstraint(
                condition=~Q(from_source=F("to_source")),
                name="source_relation_not_self",
            ),
            models.UniqueConstraint(
                fields=("from_source", "to_source", "relationship_type"),
                name="unique_directed_source_relation",
            ),
        ]

    from_source = models.ForeignKey(
        "diamm_data.Source",
        related_name="outgoing_source_relationships",
        on_delete=models.CASCADE,
    )
    to_source = models.ForeignKey(
        "diamm_data.Source",
        related_name="incoming_source_relationships",
        on_delete=models.CASCADE,
    )
    relationship_type = models.ForeignKey(
        "diamm_data.SourceToSourceRelationshipType",
        related_name="relationships",
        on_delete=models.PROTECT,
    )

    def clean(self):
        super().clean()
        if self.from_source_id == self.to_source_id:
            raise ValidationError("A source cannot be related to itself.")

    def __str__(self):
        return f"{self.from_source} — {self.relationship_type.forward_label} — {self.to_source}"
