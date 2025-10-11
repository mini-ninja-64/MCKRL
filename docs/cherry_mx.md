# Cherry MX Notes

## Stabilisers ("Leveling Mechanism")

### Nomenclature

Keyboard enthusiasts tend to use the term "stabiliser", but Cherry refers to it
as a "leveling mechanism". In their datasheets, we are given the following part
numbers for "Leveling Mechanism Kits":

<!-- markdownlint-disable-next-line -->
| Keycap Size (relative units) | 1 x 2<br>1 x 2.25<br>1 x 2.75 |    1 x 3 |    1 x 8 | 1 x 8<br>1 x 9<br>1 x 10 |    1 x 7 |
|------------------------------|------------------------------:|---------:|---------:|-------------------------:|---------:|
| Part number with frame       |                      G99-0224 | G99-0225 | G99-0226 |                 G99-0226 | G99-0379 |
| Part number without frame    |                      G99-0742 | G99-0743 | G99-0744 |                 G99-0744 | G99-0745 |

Chiefly, we are interested in the part numbers "without frame" - i.e.
"PCB-mounted" stabilisers.

The above table has several missing popular stabiliser sizes, most notably 6.00
and 6.25 unit. This is due to the fact that Cherry does not appear to provide
official measurements for these sizes in their public facing documentation.

This is interesting as Cherry has produced keyboards with both 6.00 and 6.25
unit spacebars.

Currently 6.25 unit stabilisers are included with most, if not all, aftermarket
stabiliser kits and (although less common) 6.00 unit wires are also available
via the aftermarket or by _borrowing_ them from older 6.00 unit spacebar Cherry
keyboards.

For generated stabiliser footprints we have chosen to use Cherry part numbers
where available - and when not available a `prefix` of `Cherry_G99`, as G99
appears to only be used for "leveling mechanisms" in Cherry datasheets.

### Courtyard

The generation of stabilisers adds a courtyard line around the placement of the
stabiliser footprint. This code has some predefined "magic numbers":

```py
height = 20
width = 7
stab_wire_buffer = 4
```

These measurements are in millimetres, and have been derived from measuring a
detailed 3D model against one of our generated footprints. There is some extra
space around the stabiliser wire to simplify the courtyard line.

---

## Switch Accessories

Cherry MX-style switches can have different types of accessories. Cherry
supply MX1A switches with either an LED or an in-switch diode. The housings
support either accessory, but only one can be used at once. The MX Lock LED is
only found in the now discontinued `MX1A-31xx`.

We have chosen to integrate these accessories through a generator mapping:

```text
0 1 2 3
- x x - (LED)
x - - x (Diode)
- - x x (MX Lock LED)
```

These mappings can be thought of through the following table:

| Accessory Type | Mapping  |
| -------------- | :------: |
| Diode          | `[0, 3]` |
| LED            | `[1, 2]` |
| Lock LED       | `[2, 3]` |

---

<!-- TODO: write up the unsorted notes -->

Cherry stabilisers tend to follow the pattern of 0.5u in on each side
from footprint width, e.g a 7u footprint would use a stabiliser that
is 6u (19.05\*6)mm stem to stem.

2u is a special case for stabilisers as it is to small to follow standard
0.5u off each side depending on the cherry specification you use, it will
either be reported as 23.8mm or 0.94in (23.876mm).

The stock KiCad library uses 23.8mm
<https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/master/Button_Switch_Keyboard.pretty/SW_Cherry_MX_2.00u_PCB.kicad_mod>

The "presumably" newest cherry spec listed by mouser uses 0.94in
<https://www.mouser.co.uk/datasheet/2/71/chcp_s_a0000003074_1-2262931.pdf>

The "presumably" older cherry spec uses 23.8mm
<https://web.archive.org/web/20220721191300/https://datasheet.octopart.com/MX1A-C1NW-Cherry-datasheet-15918975.pdf>

Without any evidence, my gut feeling is that it is "technically" 0.94in
but Cherry released an older version of the technical spec targeted at
Europeans that used mm.

Following the standard cherry system a 6.25u stab should be 5.25u (100.0125mm)
in width however online concensus seems to be 100mm (tolerances make everything
ok, but would still be good to know):

- WASD keycaps use 100mm, [source](https://web.archive.org/web/20220307130319/https://support.wasdkeyboards.com/hc/en-us/articles/115009701328-Keycap-Size-Compatibility)
- Ai03 plate generator uses 100mm [source](https://github.com/ai03-2725/another-keyboard-builder/blob/0f52ef2bb39afde84d08aeb9e80d962542ff5d91/plategen2.py#L273)
- Deskthority lists measurement as 100mm, [source](https://web.archive.org/web/20220216113335/https://deskthority.net/wiki/Space_bar_dimensions#6.25_units_.28118mm_wide.2C_3_mounts.2C_50mm_apart.29)
- Signature Plastics 99.7712mm, [source](https://web.archive.org/web/20220909014751/https://pimpmykeyboard.com/dcs-spacebars-pack-of-1)
- GMK was contacted [here](https://uniqey.zendesk.com/hc/en-us/requests/new) but were unable to provide their measurements due to intellectual property stuff

6u spacebars have some oddities, original cherry 6u spacebars are
designed to follow standard spacing but the mx switch was not centred.
Later revisions by GMK have updated the spacebars to support both centred
and the original offcentred 6u key and Signature Plastics spacing.

Signature Plastics 6u Specification is different to original Cherry!
Instead, bars require a stabiliser that is 76.2mm (4u) mount to mount
This spacing is also supported on some keyboards, some examples:

- Infinity Keyboard using Hacker layout
- Some older leopold keyboards, some also include both spacebars in the box
