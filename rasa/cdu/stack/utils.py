from typing import Optional, Set
from rasa.cdu.patterns.collect_information import (
    CollectInformationPatternFlowStackFrame,
)
from rasa.cdu.stack.frames import BaseFlowStackFrame
from rasa.cdu.stack.dialogue_stack import DialogueStack
from rasa.cdu.stack.frames import UserFlowStackFrame
from rasa.shared.core.flows.flow import FlowsList


def top_flow_frame(
    dialogue_stack: DialogueStack, ignore_collect_information_pattern: bool = True
) -> Optional[BaseFlowStackFrame]:
    """Returns the topmost flow frame from the tracker.

    By default, the topmost flow frame is ignored if it is the
    `pattern_collect_infomration`. This is because the `pattern_collect_information`
    is a special flow frame that is used to collect information from the user
    and commonly, is not what you are looking for when you want the topmost frame.

    Args:
        dialogue_stack: The dialogue stack to use.
        ignore_collect_information_pattern: Whether to ignore the
            `pattern_collect_information` frame.

    Returns:
        The topmost flow frame from the tracker. `None` if there
        is no frame on the stack.
    """

    for frame in reversed(dialogue_stack.frames):
        if ignore_collect_information_pattern and isinstance(
            frame, CollectInformationPatternFlowStackFrame
        ):
            continue
        if isinstance(frame, BaseFlowStackFrame):
            return frame
    return None


def top_user_flow_frame(dialogue_stack: DialogueStack) -> Optional[UserFlowStackFrame]:
    """Returns the topmost user flow frame from the tracker.

    A user flow frame is a flow defined by a bot builder. Other frame types
    (e.g. patterns, search frames, chitchat, ...) are ignored when looking
    for the topmost frame.

    Args:
        tracker: The tracker to use.


    Returns:
        The topmost user flow frame from the tracker."""
    for frame in reversed(dialogue_stack.frames):
        if isinstance(frame, UserFlowStackFrame):
            return frame
    return None


def filled_slots_for_active_flow(
    dialogue_stack: DialogueStack, all_flows: FlowsList
) -> Set[str]:
    """Get all slots that have been filled for the current flow.

    Args:
        tracker: The tracker to get the filled slots from.
        all_flows: All flows.

    Returns:
    All slots that have been filled for the current flow.
    """
    asked_collect_information = set()

    for frame in reversed(dialogue_stack.frames):
        if not isinstance(frame, BaseFlowStackFrame):
            break
        flow = frame.flow(all_flows)
        for q in flow.previously_asked_collect_information(frame.step_id):
            asked_collect_information.add(q.collect_information)

        if isinstance(frame, UserFlowStackFrame):
            # as soon as we hit the first stack frame that is a "normal"
            # user defined flow we stop looking for previously asked collect infos
            # because we only want to ask collect infos that are part of the
            # current flow.
            break

    return asked_collect_information
