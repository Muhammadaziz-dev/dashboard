from django.db import migrations, models


def migrate_attendance(apps, schema_editor):
    Record = apps.get_model('accounts', 'Record')
    # Existing data may have booleans stored as strings/ints depending on DB; map truthy to 'P', falsy to 'A'
    for r in Record.objects.all():
        try:
            val = r.attendance
            if isinstance(val, bool):
                r.attendance = 'P' if val else 'A'
            elif str(val) in ['True', '1']:
                r.attendance = 'P'
            else:
                r.attendance = 'A'
            r.save(update_fields=['attendance'])
        except Exception:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_lesson_student_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='joined_at',
            field=models.DateField(auto_now_add=True, null=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='record',
            name='attendance',
            field=models.CharField(choices=[('P', '+'), ('E', '−'), ('A', '×')], default='A', max_length=1),
        ),
        migrations.RunPython(migrate_attendance, reverse_code=migrations.RunPython.noop),
    ]

