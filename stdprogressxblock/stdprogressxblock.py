"""TO-DO: Write a description of what this XBlock is."""

import datetime
import pkg_resources
import logging
import json
import pytz

from courseware.models import StudentModule
from mako.template import Template
from webob.response import Response

from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Scope, Integer, String, Float
from xblock.fragment import Fragment

from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError

from xmodule.modulestore import ModuleStoreEnum

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from courseware.grades import yield_dynamic_descriptor_descendents as yield_descendents

log = logging.getLogger(__name__)

class StdProgXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    MODULES_TO_IGNORE = [
        "about","chapter","course","html","sequential","static_tab",
        "vertical","course_info","discussion","videoalpha","stdprogressxblock"
    ]

    display_name = String(
        display_name="Display name",
        default="Student Progress ",
        help="This name appears in the horizontal navigation at the top of "
             "the page.",
        scope=Scope.settings,
    )

    def student_view(self, context=None):
        """
        The primary view of the StdProgXBlock, shown to students
        when viewing courses.
        """
        context = {}
        progress = self.get_progress_data()
        context.update(progress)
        
        frag = Fragment()
        frag.add_content(
            render_template(
                'templates/stdprogressxblock/show.html',
                context
            )
        )

        frag.add_css(load_resource("static/css/stdprogressxblock.css"))

        frag.add_javascript(
            load_resource("static/js/src/stdprogressxblock.js")
        )

        frag.initialize_js('StdProgXBlock')
        return frag

    def get_progress_data(self):
        """
        Returns progress data for the current course and 
        current student.
        """

        xblock_locator = self.location
        vertical_location = modulestore().get_parent_location(xblock_locator)
        sequential_location = modulestore().get_parent_location(
            vertical_location
        )

        chapter_location = modulestore().get_parent_location(
            sequential_location
        )
        
        all_modules = modulestore().get_items(self.course_id, 
            revision=ModuleStoreEnum.RevisionOption.published_only)

        items_in_course = 0
        items_completed_in_course = 0

        for module_descriptor in all_modules:
            block_type = module_descriptor.scope_ids.block_type
            block_location = module_descriptor.location

            if block_type not in self.MODULES_TO_IGNORE:
                items_in_course += 1

                status = self.get_completion_status(
                    block_type, block_location
                )

                items_completed_in_course += status

        items_in_section = 0
        items_completed_in_section = 0

        submission_count = 0
        submission_completed_count = 0

        video_count = 0
        video_completed_count = 0

        problem_count = 0
        problem_completed_count = 0

        other_count = 0
        other_completed_count = 0

        chapter = modulestore().get_item(chapter_location)

        for module_descriptor in yield_descendents(chapter, None):
            block_type = module_descriptor.scope_ids.block_type
            block_location = module_descriptor.location

            if block_type not in self.MODULES_TO_IGNORE:
                items_in_section += 1

                status = self.get_completion_status(
                    block_type, block_location
                )

                items_completed_in_section += status

                if block_type in ["openassessment", "edx_sga"]:
                    submission_count += 1
                    submission_completed_count += status
                elif block_type == "video":
                    video_count += 1
                    video_completed_count += status
                elif block_type == "problem":
                    problem_count += 1
                    problem_completed_count += status
                else:
                    other_count += 1
                    other_completed_count += status

        return {
            "items_in_course": items_in_course,
            "items_completed_in_course": items_completed_in_course,
            "items_in_section": items_in_section,
            "items_completed_in_section": items_completed_in_section,
            "video_count": video_count,
            "video_completed_count": video_completed_count,
            "submission_count": submission_count,
            "submission_completed_count": submission_completed_count,
            "problem_count": problem_count,
            "problem_completed_count": problem_completed_count,
            "other_count": other_count,
            "other_completed_count": other_completed_count
        }

    def get_completion_status(self, module_type, module_id=None):
        completion_status = 0

        filter_dict = {
            'student_id': self.scope_ids.user_id,
            'course_id__contains': str(self.xmodule_runtime.course_id),
            'module_type': module_type
        }

        if module_type in ["combinedopenended", "conditional", "lti", "randomize"]:
            # Here we count all the modules whose state is valid or not null.
            filter_dict['state__isnull'] = False
        elif module_type in self.MODULES_TO_IGNORE:
            # Do nothing for these modules.
            pass
        elif module_type == "edx_sga":
            # courseware_studentmodule.state contains a valid uploaded_timestamp.
            filter_dict['state__contains'] = "uploaded_timestamp"
        elif module_type == "flexible_grader":
            # If a grade has been received.
            filter_dict["state__contains"] = "comment"
        elif module_type == "problem":
            # Module state is valid contain done:true.
            filter_dict["state__contains"] = "done"
        elif  module_type == "openassessment":
            # Module state contain a valid submission_uuid.
            filter_dict["state__contains"] = "submission_uuid"
        elif module_type == "video":
            pass
        else:
             # All other types of modules.
             filter_dict["state__isnull"] = False

        if module_id:
            filter_dict["module_state_key"] = module_id

        modules_count = StudentModule.objects.filter(**filter_dict).count()
        completion_status = modules_count

        return completion_status

def load_resource(resource_path):
    """
    Gets the content of a resource
    """
    resource_content = pkg_resources.resource_string(__name__, resource_path)
    return resource_content.decode("utf8")

def render_template(template_path, context={}):
    """
    Evaluate a template by resource path, applying the provided context
    """
    template_str = load_resource(template_path)
    template = Template(template_str)
    return template.render(**context)