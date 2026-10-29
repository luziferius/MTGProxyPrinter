"""Pure mark geometry/clearance checks; read existing evidence without rebuilding it."""
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path

import pytest

from mtg_proxy_printer.model.page_geometry import CardPlacement, Rectangle, SideDistances, build_page_geometry
from mtg_proxy_printer.model.page_layout import PageLayoutSettings
from mtg_proxy_printer.siser_page_marks import (
    MarkClearanceIssue, RegistrationBar, SiserPageMarks,
    assess_siser_clearance, build_siser_page_marks,
)
from mtg_proxy_printer.units_and_sizes import PageType, distance_to_px, unit_registry

mm = unit_registry.mm
EVIDENCE = Path(__file__).parent / 'data/print_cut/siser'
IDS = tuple(f'{corner}-{direction}' for corner in
            ('top-left','top-right','bottom-left','bottom-right') for direction in ('horizontal','vertical'))


def values(rect):
    return rect.x, rect.y, rect.width, rect.height


def letter(count=9, **kwargs):
    return build_page_geometry(PageLayoutSettings(paper_size='Letter',paper_orientation='Portrait',
        margin_left=0*mm,margin_top=0*mm,margin_right=0*mm,margin_bottom=0*mm,
        row_spacing=0*mm,column_spacing=0*mm,**kwargs),PageType.REGULAR,count)


def synthetic(rects):
    placements = tuple(CardPlacement(slot,0,0,Rectangle(*(distance_to_px(v*mm) for v in values(rect))),
                                    SideDistances(0,0,0,0)) for slot,rect in rects)
    return replace(letter(0),placements=placements)


def test_stable_ids_order_and_independent_letter_coordinates():
    marks = build_siser_page_marks(215.9,279.4)
    assert tuple(b.bar_id for b in marks.bars) == IDS
    expected = [(6,5.5,13,1),(5.5,6,1,13),(196.9,5.5,13,1),(209.4,6,1,13),
                (6,272.9,13,1),(5.5,260.4,1,13),(196.9,272.9,13,1),(209.4,260.4,1,13)]
    for bar,wanted in zip(marks.bars,expected):
        assert values(bar.bounds_mm) == pytest.approx(wanted,abs=1e-12,rel=0)
    assert marks == build_siser_page_marks(215.9,279.4)
    assert isinstance(marks.bars,tuple)
    with pytest.raises(FrozenInstanceError):
        marks.frame_width_mm = 1
    with pytest.raises(FrozenInstanceError):
        marks.bars[0].bar_id = 'changed'
    with pytest.raises(FrozenInstanceError):
        marks.bars[0].bounds_mm.x = 1


@pytest.mark.parametrize('reference',['m08b-letter','m08a-letter','m08a-a4'])
def test_direct_reference_agreement(reference):
    if reference == 'm08b-letter':
        record = json.loads((EVIDENCE/'references/external-marks/nine-card-baseline/reference.json').read_text())
        frame = record['requested_paper_mm']
        measured = record['measurement']['bars']
    else:
        record = json.loads((EVIDENCE/'numeric-placement-measurements.json').read_text())
        name = 'letter-base-initial' if reference == 'm08a-letter' else 'a4-page-before-import'
        output = next(o for o in record['outputs'] if o['id'] == name)
        frame = output['emitted_page_mm']  # Full recorded precision, never the nominal A4 sheet.
        measured = output['registration_bars']
    wanted = sorted(tuple(b['bounds_xywh_mm']) for b in measured)
    actual = sorted(values(b.bounds_mm) for b in build_siser_page_marks(*frame).bars)
    assert len(wanted) == len(actual) == 8
    for a,b in zip(actual,wanted):
        assert a == pytest.approx(b,abs=.001,rel=0)
    if reference == 'm08a-a4':
        geometry = build_page_geometry(PageLayoutSettings(paper_size='A4',paper_orientation='Landscape'),PageType.REGULAR,1)
        assert (geometry.sheet_width_mm,geometry.sheet_height_mm) == (297,210)
        assert tuple(frame) != (297,210)
        before = geometry
        assess_siser_clearance(geometry,build_siser_page_marks(*frame))
        assert geometry == before


@pytest.mark.parametrize('frame',[(210,297),(297,210),(304.8,203.2),(100.123456789,140.987654321),(38.0001,38.0001)])
def test_mathematical_frames_and_axis_changes(frame):
    marks = build_siser_page_marks(*frame)
    for dimension in (0,1):
        changed = list(frame); changed[dimension] += 17.123456789
        other = build_siser_page_marks(*changed)
        for a,b in zip(marks.bars,other.bars):
            moved = ('right' in a.bar_id) if dimension == 0 else ('bottom' in a.bar_id)
            delta = [0.,0.,0.,0.]; delta[dimension] = 17.123456789 if moved else 0.
            assert tuple(y-x for x,y in zip(values(a.bounds_mm),values(b.bounds_mm))) == pytest.approx(delta,abs=1e-12,rel=0)
    assert values(marks.bars[0].bounds_mm) == (6,5.5,13,1)


def test_dense_letter_bleed_and_separated_layout_without_mark_motion():
    marks = build_siser_page_marks(215.9,279.4)
    baseline = letter()
    assert assess_siser_clearance(baseline,marks) == ()
    bled = letter(card_bleed=1.5*mm)
    # Existing canonical rounding is authoritative: 18 px = 1.524 mm, not 1.5.
    assert bled.placements[0].bleed_mm.top == pytest.approx(1.524,abs=1e-12,rel=0)
    issues = assess_siser_clearance(bled,marks)
    collisions = {(i.slot_index,i.bar_id) for i in issues if i.code == 'printed_envelope_intersects_mark'}
    assert collisions == {(0,'top-left-horizontal'),(2,'top-right-horizontal'),
                          (6,'bottom-left-horizontal'),(8,'bottom-right-horizontal')}
    separated = build_page_geometry(PageLayoutSettings(paper_size='Letter',margin_left=12*mm,
        margin_top=12*mm,margin_right=12*mm,margin_bottom=12*mm,card_bleed=1.5*mm),PageType.REGULAR,4)
    assert assess_siser_clearance(separated,marks) == ()
    assert marks == build_siser_page_marks(215.9,279.4)


def test_layout_and_corner_changes_affect_only_envelopes_not_marks():
    from mtg_proxy_printer.trim_contour import trim_contour
    marks = build_siser_page_marks(215.9,279.4)
    layouts = [PageLayoutSettings(paper_size='Letter',row_spacing=2*mm,column_spacing=2*mm),
               PageLayoutSettings(paper_size='Letter',margin_top=12*mm,margin_left=12*mm),
               PageLayoutSettings(paper_size='Letter',draw_sharp_corners=True,card_bleed=1.5*mm)]
    results = [assess_siser_clearance(letter(),marks)]
    for layout in layouts:
        geometry = build_page_geometry(layout,PageType.REGULAR,1)
        original = geometry
        trim_contour(geometry.placements[0].trim_mm,geometry.page_type)
        results.append(assess_siser_clearance(geometry,marks))
        assert geometry == original
        assert marks == build_siser_page_marks(215.9,279.4)
    assert any(result != results[0] for result in results[1:])
    g = letter()
    assert assess_siser_clearance(replace(g,page_type=PageType.OVERSIZED),marks) == assess_siser_clearance(g,marks)


@pytest.mark.parametrize('x,padding,code',[
    (18,0,'printed_envelope_intersects_mark'),
    (19,0,'printed_envelope_intersects_mark'),
    (19+2e-9,0,None),
    (20,1,'printed_envelope_within_requested_clearance'),
    (20+2e-9,1,None),
    (19,5,'printed_envelope_intersects_mark'),
])
def test_overlap_touch_padding_and_just_outside(x,padding,code):
    marks = SiserPageMarks(215.9,279.4,(RegistrationBar('test',Rectangle(6,5.5,13,1)),))
    geometry = synthetic([(7,Rectangle(x,5.5,2,1))])
    wanted = () if code is None else (MarkClearanceIssue(code,7,'test'),)
    assert assess_siser_clearance(geometry,marks,extra_clearance_mm=padding) == wanted


def test_l_mark_empty_interior_and_axis_aligned_padding():
    marks = build_siser_page_marks(215.9,279.4)
    g = synthetic([(3,Rectangle(8,8,1,1))])
    assert assess_siser_clearance(g,marks) == ()  # Inside L bounding box, outside ink.
    padded = assess_siser_clearance(g,marks,extra_clearance_mm=2)
    assert padded == tuple(MarkClearanceIssue('printed_envelope_within_requested_clearance',3,bar)
                          for bar in ('top-left-horizontal','top-left-vertical'))
    # Diagonal corner lies within rectangular padding despite radial distance > 2.
    one = SiserPageMarks(100,100,(RegistrationBar('one',Rectangle(20,20,1,1)),))
    diagonal = synthetic([(1,Rectangle(22.9,22.9,1,1))])
    assert assess_siser_clearance(diagonal,one,extra_clearance_mm=2)


def test_empty_partial_and_issue_attribution_order_without_mutation():
    marks = build_siser_page_marks(215.9,279.4)
    assert assess_siser_clearance(letter(0),marks,extra_clearance_mm=10) == ()
    assert not any(i.slot_index != 0 for i in assess_siser_clearance(letter(1,card_bleed=1.5*mm),marks))
    g = synthetic([(9,Rectangle(-1,5.5,10,1)),(2,Rectangle(6,5.5,1,1))])
    out = SiserPageMarks(215.9,279.4,(RegistrationBar('outside',Rectangle(-1,5.5,1,1)),
                                       RegistrationBar('inside',Rectangle(6,5.5,1,1))))
    original = (g,out)
    issues = assess_siser_clearance(g,out)
    assert issues == (MarkClearanceIssue('registration_bar_outside_sheet',None,'outside'),
        MarkClearanceIssue('printed_envelope_outside_sheet',9,None),
        MarkClearanceIssue('printed_envelope_intersects_mark',9,'outside'),
        MarkClearanceIssue('printed_envelope_intersects_mark',9,'inside'),
        MarkClearanceIssue('printed_envelope_intersects_mark',2,'inside'))
    assert issues == assess_siser_clearance(g,out)
    assert (g,out) == original
    # Outside diagnostics use the nominal sheet, not registration-frame dimensions.
    assert len(assess_siser_clearance(letter(0),build_siser_page_marks(300,400))) == 6
    assert assess_siser_clearance(synthetic([(0,Rectangle(0,0,215.9,279.4))]),SiserPageMarks(215.9,279.4,())) == ()


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-float('inf'),0,-1,38,37.99,None,'210',True,10**400])
@pytest.mark.parametrize('axis',[0,1])
def test_invalid_frame(value,axis):
    dims = [215.9,279.4]; dims[axis] = value
    with pytest.raises(ValueError,match='exceed 38'):
        build_siser_page_marks(*dims)


@pytest.mark.parametrize('value',[float('nan'),float('inf'),-float('inf'),-1,None,'1',True,1.7e308,10**400])
def test_invalid_padding_or_derived_overflow(value):
    with pytest.raises(ValueError):
        assess_siser_clearance(letter(0),build_siser_page_marks(215.9,279.4),extra_clearance_mm=value)


def test_invalid_supplied_sheet_bar_and_envelope_fail_clearly():
    marks = build_siser_page_marks(215.9,279.4)
    with pytest.raises(ValueError,match='sheet dimensions'):
        assess_siser_clearance(replace(letter(0),sheet_width_mm=float('nan')),marks)
    with pytest.raises(ValueError,match='Rectangle bounds'):
        assess_siser_clearance(letter(0),SiserPageMarks(215.9,279.4,
            (RegistrationBar('bad',Rectangle(1.7e308,0,1.7e308,1)),)))
    g = replace(letter(1),placements=(replace(letter(1).placements[0],trim_px=Rectangle(float('nan'),0,10,10)),))
    with pytest.raises(ValueError,match='Rectangle bounds'):
        assess_siser_clearance(g,marks)
