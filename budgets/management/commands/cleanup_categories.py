from django.core.management.base import BaseCommand

from budgets.models import Category, MLCategoryTrainingData, TransactionRecord


class Command(BaseCommand):
    help = "사용자에게 중복 생성된 기본 카테고리를 공용 기본 카테고리로 병합합니다."

    def handle(self, *args, **options):
        deleted_count = 0
        updated_count = 0

        duplicates = Category.objects.filter(user__isnull=False, is_default=True)

        for duplicate in duplicates:
            default_category = Category.objects.filter(
                user__isnull=True,
                name=duplicate.name,
                type=duplicate.type,
            ).first()

            if default_category is None:
                duplicate.user = None
                duplicate.save(update_fields=["user"])
                updated_count += 1
                continue

            TransactionRecord.objects.filter(category=duplicate).update(
                category=default_category
            )
            MLCategoryTrainingData.objects.filter(category=duplicate).update(
                category=default_category
            )
            duplicate.delete()
            deleted_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"중복 카테고리 {deleted_count}개를 삭제하고 "
                f"기본 카테고리 {updated_count}개를 공용으로 변경했습니다."
            )
        )
