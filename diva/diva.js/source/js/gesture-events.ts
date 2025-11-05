import {Offset, PageXYPos} from "./viewer-type-definitions";

export default {
    onDoubleClick,
    onPinch,
    onDoubleTap
};

const DOUBLE_CLICK_TIMEOUT = 500;
const DOUBLE_TAP_DISTANCE_THRESHOLD = 50;
const DOUBLE_TAP_TIMEOUT = 250;

function onDoubleClick(elem: HTMLElement, callback: (arg0: MouseEvent, arg1: { top: number; left: number; }) => void)
{
    elem.addEventListener('dblclick', function (event)
    {
        if (!event.ctrlKey)
        {
            callback(event, getRelativeOffset(event.currentTarget as HTMLElement, event));
        }
    });

    // Handle the control key for macs (in conjunction with double-clicking)
    // FIXME: Does a click get handled with ctrl pressed on non-Macs?
    const tracker = createDoubleEventTracker(DOUBLE_CLICK_TIMEOUT);

    elem.addEventListener('contextmenu', function (event)
    {
        event.preventDefault();

        if (event.ctrlKey)
        {
            if (tracker.isTriggered())
            {
                tracker.reset();
                callback(event, getRelativeOffset(event.currentTarget as HTMLElement, event));
            }
            else
            {
                tracker.trigger();
            }
        }
    });
}

function onPinch(elem: HTMLElement, callback: any)
{
    let startDistance = 0;

    elem.addEventListener('touchstart', function (event: TouchEvent)
    {
        // Prevent mouse event from firing
        event.preventDefault();

        if (event.touches.length === 2)
        {
            startDistance = distance(
                event.touches[0].clientX,
                event.touches[0].clientY,
                event.touches[1].clientX,
                event.touches[1].clientY
            );
        }
    });

    elem.addEventListener('touchmove', function(event: TouchEvent)
    {
        // Prevent mouse event from firing
        event.preventDefault();

        if (event.touches.length === 2)
        {
            const touches = event.touches;

            const moveDistance = distance(
                touches[0].clientX,
                touches[0].clientY,
                touches[1].clientX,
                touches[1].clientY
            );

            const zoomDelta = moveDistance - startDistance;

            if (Math.abs(zoomDelta) > 0)
            {
                const touchCenter = {
                    pageX: (touches[0].clientX + touches[1].clientX) / 2,
                    pageY: (touches[0].clientY + touches[1].clientY) / 2
                };

                callback(event, getRelativeOffset(event.currentTarget as HTMLElement, touchCenter), startDistance, moveDistance);
            }
        }
    });
}

function onDoubleTap(elem: HTMLElement, callback: any)
{
    const tracker = createDoubleEventTracker(DOUBLE_TAP_TIMEOUT);
    let firstTap: PageXYPos | null = null;

    elem.addEventListener('touchend', (event) =>
    {
        // Prevent mouse event from firing
        event.preventDefault();

        if (tracker.isTriggered())
        {
            tracker.reset();

            // Doubletap has occurred
            const secondTap = {
                pageX: event.changedTouches[0].clientX,
                pageY: event.changedTouches[0].clientY
            };

            // If first tap is close to second tap (prevents interference with scale event)
            const tapDistance = distance(firstTap!.pageX, firstTap!.pageY, secondTap.pageX, secondTap.pageY);

            // TODO: Could give something higher-level than secondTap to callback
            if (tapDistance < DOUBLE_TAP_DISTANCE_THRESHOLD)
            {
                callback(event, getRelativeOffset(event.currentTarget as HTMLElement, secondTap));
            }

            firstTap = null;
        }
        else
        {
            firstTap = {
                pageX: event.changedTouches[0].clientX,
                pageY: event.changedTouches[0].clientY
            };

            tracker.trigger();
        }
    });
}

// Pythagorean theorem to get the distance between two points (used for
// calculating finger distance for double-tap and pinch-zoom)
function distance(x1: number, y1: number, x2: number, y2: number): number
{
    return Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
}

// Utility to keep track of whether an event has been triggered twice
// during a a given duration
function createDoubleEventTracker(timeoutDuration: number)
{
    let triggered = false;
    let timeoutId: number | null = null;

    return {
        trigger()
        {
            triggered = true;
            resetTimeout();
            timeoutId = setTimeout(function ()
            {
                triggered = false;
                timeoutId = null;
            }, timeoutDuration);
        },
        isTriggered()
        {
            return triggered;
        },
        reset()
        {
            triggered = false;
            resetTimeout();
        }
    };

    function resetTimeout()
    {
        if (timeoutId !== null)
        {
            clearTimeout(timeoutId);
            timeoutId = null;
        }
    }
}

function getRelativeOffset(elem: HTMLElement, pageCoords: {pageX: number, pageY: number}): Offset
{
    const bounds = elem.getBoundingClientRect();

    return {
        left: pageCoords.pageX - bounds.left,
        top: pageCoords.pageY - bounds.top
    };
}
