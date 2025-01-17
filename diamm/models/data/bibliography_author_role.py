from django.db import models


class BibliographyAuthorRole(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ("position",)

    R_AUTHOR = 1
    R_EDITOR = 2
    R_COMPILER = 3
    R_FESTSCHRIFT = 4
    R_COLLABORATOR = 5
    R_INDEXER = 6
    R_LATER_EDITOR = 7
    R_PUBLISHER = 8
    R_REVIEWER = 9
    R_REVISER = 10
    R_SUPERVISOR = 11
    R_TRANSLATOR = 12
    R_COPYIST = 13

    ROLES = (
        (R_AUTHOR, "Author"),
        (R_EDITOR, "Editor"),
        (R_COMPILER, "Compiler"),
        (R_FESTSCHRIFT, "Festschrift Dedicatee"),
        (R_COLLABORATOR, "Collaborator"),
        (R_INDEXER, "Indexer"),
        (R_LATER_EDITOR, "Later Editor"),
        (R_PUBLISHER, "Publisher"),
        (R_REVIEWER, "Reviewer"),
        (R_REVISER, "Reviser"),
        (R_SUPERVISOR, "Supervisor"),
        (R_TRANSLATOR, "Translator"),
        (R_COPYIST, "Copyist"),
    )

    bibliography_author = models.ForeignKey(
        "diamm_data.BibliographyAuthor",
        related_name="bibliography_entries",
        on_delete=models.CASCADE,
    )
    bibliography_entry = models.ForeignKey(
        "diamm_data.Bibliography", related_name="authors", on_delete=models.CASCADE
    )
    role = models.IntegerField(choices=ROLES)
    position = models.IntegerField(
        default=1, help_text="""The position of this author in the author list."""
    )

    def __str__(self):
        return f"{self.bibliography_author}"
