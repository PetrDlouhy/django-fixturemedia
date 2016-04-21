"""Module of management command 'collectmedia'."""

from optparse import make_option
import os
from shutil import copy

from django.apps import apps
from django.core.management.base import CommandError, NoArgsCommand

from ._utils import file_patt, file_patt_prefixed


class Command(NoArgsCommand):
    """Management command to collect media files."""

    can_import_settings = True
    opt = make_option('--noinput',
                      action='store_false',
                      dest='interactive',
                      default=True,
                      help='Do NOT prompt the user for input of any kind.')
    option_list = NoArgsCommand.option_list + (opt, )

    def handle_noargs(self, **options):
        """Handle command invocation."""
        from django.conf import settings
        fixtures = self.find_fixtures(settings.FIXTURE_DIRS)
        if options['interactive']:
            msg = 'This will overwrite any existing files. Proceed? '
            confirm = input(msg)
            if not confirm.lower().startswith('y'):
                raise CommandError('Media synchronization aborted')
        if getattr(settings, 'FIXTURE_MEDIA_REQUIRE_PREFIX', False):
            self.pattern = file_patt_prefixed
        else:
            self.pattern = file_patt
        for root, fixture in fixtures:
            self.handle_fixture(root,
                                fixture,
                                settings.MEDIA_ROOT,
                                options['verbosity'])

    def handle_fixture(self, root, fixture, media_root, verbosity=0):
        """Copy media files to MEDIA_ROOT."""
        file_paths = self.pattern.findall(open(fixture).read())
        if file_paths:
            for fp in file_paths:
                fixture_path = os.path.join(root, 'media', fp)
                if not os.path.exists(fixture_path):
                    if int(verbosity) >= 1:
                        msg = ('File path ({}) found in fixture '
                               'but not on disk in ({}) \n')
                        self.stderr.write(msg.format(fp, fixture_path))
                    continue
                final_dest = os.path.join(media_root, fp)
                dest_dir = os.path.dirname(final_dest)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                msg = 'Copied {} to {}\n'
                self.stdout.write(msg.format(fp, final_dest))
                copy(fixture_path, final_dest)

    def find_fixtures(self, fixture_dirs):
        """Find fixtures in installed applications."""
        app_module_paths = []
        for app in apps.get_app_configs():
            if hasattr(app, '__path__'):
                # It's a 'models/' sub-package
                for path in app.__path__:
                    app_module_paths.append(path)
            else:
                # It's a models.py module
                app_module_paths.append(app.__file__)
        pathl = lambda path: os.path.join(os.path.dirname(path), 'fixtures')
        app_fixtures = [pathl(path) for path in app_module_paths]
        app_fixtures += list(fixture_dirs) + ['']
        fixtures = []
        for fixture_path in app_fixtures:
            try:
                root, _, files = os.walk(fixture_path).next()
                for file in files:
                    if file.rsplit('.', 1)[-1] in ('json', 'yaml'):
                        fixtures.append((root, os.path.join(root, file)))
            except StopIteration:
                pass
        return fixtures
