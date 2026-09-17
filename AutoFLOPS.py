import re
import shutil
import os
import argparse


def update_flops_file(
    source_file:  str,
    dest_dir:     str,
    new_name:     str,
    DOWE:         float = None,
    DNAC:         float = None,
    XNAC:         float = None,
    THRUST:       float = None,
    THRSO:        float = None,
    EIFILE:       str   = None,
):
    """
    Copy a FLOPS input file, update specified values via regex, and move to destination.

    Parameters
    ----------
    source_file : str   - Path to the original FLOPS input file
    dest_dir    : str   - Directory to move the final updated file to
    new_name    : str   - New filename for the copied file
    DOWE        : float - Operating weight empty (lbs)
    DNAC        : float - Nacelle diameter
    XNAC        : float - Nacelle X location
    THRUST      : float - Thrust per engine (lbs)
    THRSO       : float - Sea level static thrust (lbs)
    EIFILE      : str   - Engine deck file name (e.g. 'engine4.deck')
    """

    # ── Step 1: Copy file to same directory with new name ─────────────────────
    source_dir   = os.path.dirname(os.path.abspath(source_file))
    copied_file  = os.path.join(source_dir, new_name)

    shutil.copy2(source_file, copied_file)
    print(f"Copied '{source_file}' → '{copied_file}'")

    # ── Step 2: Read copied file ──────────────────────────────────────────────
    with open(copied_file, 'r') as f:
        content = f.read()

    # ── Step 3: Update values via regex ──────────────────────────────────────
    def replace_value(text, key, new_val):
        """Replace key = <old_value> with key = <new_value> in FLOPS namelist format."""
        if new_val is None:
            return text

        if isinstance(new_val, str):
            # String value — wrap in single quotes (e.g. EIFILE = 'engine4.deck')
            pattern     = rf"({re.escape(key)}\s*=\s*')[^']*(')"
            replacement = rf"\g<1>{new_val}\g<2>"
        else:
            # Numeric value
            pattern     = rf"({re.escape(key)}\s*=\s*)[\d.]+"
            replacement = rf"\g<1>{new_val}"

        updated, count = re.subn(pattern, replacement, text)

        if count == 0:
            print(f"  [WARNING] '{key}' not found in file — no replacement made")
        else:
            print(f"  Updated  {key:10s} = {new_val}")

        return updated

    updates = {
        'DOWE'  : DOWE,
        'DNAC'  : DNAC,
        'XNAC'  : XNAC,
        'THRUST': THRUST,
        'THRSO' : THRSO,
        'EIFILE': EIFILE,
    }

    print("\nApplying updates:")
    for key, val in updates.items():
        content = replace_value(content, key, val)

    # ── Step 4: Write updated content back to copied file ─────────────────────
    with open(copied_file, 'w') as f:
        f.write(content)
    print(f"\nUpdated file written to '{copied_file}'")

    # ── Step 5: Move file to destination directory ─────────────────────────────
    os.makedirs(dest_dir, exist_ok=True)
    final_path = os.path.join(dest_dir, new_name)
    shutil.move(copied_file, final_path)
    print(f"Moved file → '{final_path}'")

    return final_path


# ══════════════════════════════════════════════════════════════════════════════
# Command line interface
# ══════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description='Update FLOPS input file values and move to a new location.'
    )

    # ── Required arguments ────────────────────────────────────────────────────
    parser.add_argument('source_file', type=str,
                        help='Path to the original FLOPS input file')
    parser.add_argument('dest_dir',   type=str,
                        help='Destination directory for the updated file')
    parser.add_argument('new_name',   type=str,
                        help='New filename for the copied file')

    # ── Optional update arguments ─────────────────────────────────────────────
    parser.add_argument('--DOWE',   type=float, default=None, help='Operating weight empty (lbs)')
    parser.add_argument('--DNAC',   type=float, default=None, help='Nacelle diameter')
    parser.add_argument('--XNAC',   type=float, default=None, help='Nacelle X location')
    parser.add_argument('--THRUST', type=float, default=None, help='Thrust per engine (lbs)')
    parser.add_argument('--THRSO',  type=float, default=None, help='Sea level static thrust (lbs)')
    parser.add_argument('--EIFILE', type=str,   default=None, help='Engine deck filename')

    return parser.parse_args()


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    args = parse_args()

    final_path = update_flops_file(
        source_file = args.source_file,
        dest_dir    = args.dest_dir,
        new_name    = args.new_name,
        DOWE        = args.DOWE,
        DNAC        = args.DNAC,
        XNAC        = args.XNAC,
        THRUST      = args.THRUST,
        THRSO       = args.THRSO,
        EIFILE      = args.EIFILE,
    )

    print(f"\nDone. Final file: '{final_path}'")