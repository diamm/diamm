from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from diamm.helpers.solr_helpers import SolrManager


class NumberingSystemChoices(models.IntegerChoices):
    MIXED = 1, "Mixed Foliation and Pagination"
    FOLIATION = 2, "Foliation"
    PAGINATION = 3, "Pagination"
    NO_NUMBERING_SYSTEM = 4, "None / Unknown"


class SurfaceOptionChoices(models.IntegerChoices):
    PARCHMENT = 1, "Parchment"
    PAPER = 2, "Paper"
    VELLUM = 3, "Vellum"
    WOOD = 4, "Wood"
    SLATE = 5, "Slate"
    MIXED = 6, "Mixed Paper and Parchment"
    OTHER = 7, "Other"


class OriginalFormatChoices(models.IntegerChoices):
    ROTULUS = 1, "Rotulus"
    CODEX = 2, "Codex"
    LIBELLUS = 3, "Libellus"
    UNKNOWN = 4, "Unknown"


class CurrentStateChoices(models.IntegerChoices):
    FRAGMENT = 1, "Fragment"
    COMPLETE = 2, "Complete"
    LOST = 3, "Lost"


class CurrentHostChoices(models.IntegerChoices):
    REMOVED_FROM_HOST = 1, "Removed from host manuscript"
    STILL_WITH_HOST = 2, "Still within host manuscript"
    FRAGMENT_COLLECTION = 3, "Within fragment collection"


class Source(models.Model):
    class Meta:
        app_label = "diamm_data"
        ordering = ["archive__siglum", "sort_order"]

    HELP_INVENTORY = """Use this checkbox to mark whether DIAMM has provided an inventory for this
    source. Note that if there are items attached to this source they will still appear, but there will be a note on
    the source record stating that DIAMM has not provided an inventory."""

    id = models.AutoField(primary_key=True)  # migrate old ID
    archive = models.ForeignKey(
        "diamm_data.Archive", related_name="sources", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    shelfmark = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="""A brief description of the source, e.g, 'chant book with added polyphony'""",
    )
    surface = models.IntegerField(
        choices=SurfaceOptionChoices.choices, blank=True, null=True
    )
    inventory_provided = models.BooleanField(default=False, help_text=HELP_INVENTORY)

    start_date = models.IntegerField(
        blank=True,
        null=True,
        help_text="""Enter the start year as a four digit integer. If
                    the precise year is not known, enter it rounding DOWN to the closest
                    known decade, and then century. Examples: 1456, 1450, 1400.""",
    )
    end_date = models.IntegerField(
        blank=True,
        null=True,
        help_text="""Enter the end year as a four digit integer. If the
                     precise year is not known, enter it rounding UP to the
                     closest known decade, and then century. Examples: 1456, 1460, 1500.
                     """,
    )
    date_statement = models.CharField(max_length=512, blank=True, null=True)
    cover_image = models.ForeignKey(
        "diamm_data.Image", blank=True, null=True, on_delete=models.CASCADE
    )
    format = models.CharField(max_length=255, blank=True, null=True)
    measurements = models.CharField(max_length=512, blank=True, null=True)
    numbering_system = models.IntegerField(
        choices=NumberingSystemChoices.choices, blank=True, null=True
    )
    has_medieval_foliation = models.BooleanField(
        default=False, help_text="Is the foliation in use from the medieval period?"
    )
    original_format = models.IntegerField(
        choices=OriginalFormatChoices.choices, blank=True, null=True
    )
    original_format_uncertain = models.BooleanField(default=False)

    current_state = models.IntegerField(
        choices=CurrentStateChoices.choices, blank=True, null=True
    )

    current_host = models.IntegerField(
        choices=CurrentHostChoices.choices, blank=True, null=True
    )

    public = models.BooleanField(
        default=False, help_text="Source Description is Public"
    )

    public_images = models.BooleanField(
        default=False, help_text="Source Images are Public (with login)"
    )
    open_images = models.BooleanField(
        default=False, help_text="Source Images are available without login"
    )
    notations = models.ManyToManyField(
        "diamm_data.Notation", blank=True, related_name="sources"
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    sort_order = models.IntegerField(blank=True, null=True)
    contributions = GenericRelation("diamm_site.ProblemReport")
    commentary = GenericRelation("diamm_site.Commentary")

    def __str__(self) -> str:
        name: str = f" ({self.name})" if self.name else ""
        return f"{self.shelfmark}{name}"

    def get_absolute_url(self) -> str:
        return reverse("source-detail", kwargs={"pk": self.pk})

    @cached_property
    def display_name(self) -> str:
        return f"{self.archive.siglum} {str(self)}"

    @cached_property
    def display_summary(self) -> str:
        date_stmt = self.date_statement if self.date_statement else ""
        summary = self.display_name if self.display_name else ""

        if date_stmt:
            summary = f"{summary}; {date_stmt}"

        if self.notes.filter(type=1).exists():
            summary = f"{summary}; {self.notes.filter(type=1).first().note}"

        return summary

    @property
    def surface_type(self) -> str | None:
        if not self.surface:
            return None

        d = dict(SurfaceOptionChoices.choices)
        return d[self.surface]

    @property
    def numbering_system_type(self) -> str | None:
        if not self.numbering_system:
            return None
        d = dict(NumberingSystemChoices.choices)
        return d[self.numbering_system]

    @cached_property
    def cover(self):
        """
        If a cover image is set, returns the ID for that; else it chooses a random page with an image attached.
        """
        if not self.public_images:
            return None

        if not self.pages.exists():
            return None

        cover_obj = {}
        if self.cover_image:
            cover_obj["id"] = self.cover_image.id
            cover_obj["label"] = self.cover_image.page.numeration
            return cover_obj

        cover = (
            self.pages.filter(images__type=1, images__location__isnull=False)
            .order_by("?")
            .first()
        )

        if cover:
            return {"id": cover.images.first().pk, "label": cover.numeration}
        return None

    @property
    def compositions(self):
        composition_names = (
            self.inventory.filter(composition__isnull=False)
            .select_related("composition")
            .values_list("composition__title", flat=True)
        )
        return list(set(composition_names))

    @property
    def num_compositions(self) -> int:
        return self.inventory.filter(composition__isnull=False).count()

    @property
    def solr_bibliography(self) -> list:
        # Grab a list of the ids for this record
        connection = SolrManager(settings.SOLR["SERVER"])
        fq = ["type:bibliography", f"sources_ii:{self.pk}"]
        connection.search("*:*", fq=fq, sort="year_ans desc, sort_ans asc")

        if connection.hits == 0:
            return []

        reslist = []
        for res in connection.results:
            if "sources_json" in res:
                entry = [
                    s for s in res["sources_json"] if s and s["source_id"] == self.pk
                ]
                if not entry:
                    continue
                res["primary_study"] = entry[0]["primary_study"]
                if p := entry[0].get("pages"):
                    res["pages"] = p
                if n := entry[0].get("notes"):
                    res["notes"] = n
            reslist.append(res)

        return reslist
