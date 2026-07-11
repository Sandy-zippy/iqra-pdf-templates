/**
 * hydrate-loops.mjs — populate register/loop bodies for a flat single-record render.
 *
 * The U2 register forms (Drawing / Document / Readiness) and IMIR carry their
 * line-item data as flat top-level fields, but the templates render those lines
 * inside {{#drawings}} / {{#documents}} / {{#items}} / {{#photos}} loops. A flat
 * render leaves the arrays undefined so the loop bodies come out empty.
 *
 * This wraps the record's own line fields into the 1-element array each loop
 * expects. Only touches loops the template actually references and that don't
 * already carry an array (so real multi-line joins pass through untouched).
 */

// Register loops: self-wrap the record as one line. `alias` maps a loop field
// name that differs from the flat record's field name. Everything else resolves
// straight from the record because the mustache lookup walks the parent context.
const REGISTER_LOOPS = {
  drawings: { drawing_no: 'assembly_drawing_number' },
  documents: null, // field names already match the flat record
  items: null,     // readiness_item_number / readiness_item / ... match
};

function has(tpl, loop) {
  return tpl.includes('{{#' + loop + '}}');
}

// IMIR photo evidence: build one card per upload/photo attachment group, feeding
// each group's ocr_status / ocr_confidence into the field names the template card
// hardcodes (mtc_tc_upload_ocr_status / mtc_tc_upload_ocr_confidence).
function buildImirPhotos(d) {
  const groups = [
    ['mtc_tc_upload', 'MTC / TC Upload'],
    ['material_identification_photo', 'Material Identification Photo'],
    ['physical_condition_photo', 'Physical Condition Photo'],
    ['invoice_challan_upload', 'Invoice / Challan Upload'],
  ];
  const out = [];
  for (const [key, title] of groups) {
    const att = d[key];
    const status = d[key + '_ocr_status'];
    const conf = d[key + '_ocr_confidence'];
    if (att == null && status == null && conf == null) continue;
    const file = Array.isArray(att) && att[0] ? (att[0].filename || att[0].url || 'attachment') : '—';
    out.push({
      title,
      filename: file,
      captured_at: d.activity_date || d.submission_date || '',
      mtc_tc_upload_ocr_confidence: conf,
      mtc_tc_upload_ocr_status: status,
      note: d.extracted_mtc_tc_no_date || d.extracted_heat_lot_batch_no || '',
    });
  }
  return out;
}

export function hydrateLoops(data, tpl) {
  for (const [loop, alias] of Object.entries(REGISTER_LOOPS)) {
    if (!has(tpl, loop) || Array.isArray(data[loop])) continue;
    const line = { ...data };
    if (alias) for (const [to, from] of Object.entries(alias)) line[to] = data[from];
    data[loop] = [line];
  }
  if (has(tpl, 'photos') && !Array.isArray(data.photos)) {
    const photos = buildImirPhotos(data);
    if (photos.length) data.photos = photos;
  }
  return data;
}

// ponytail: self-check — run `node hydrate-loops.mjs` to verify.
if (import.meta.url === `file://${process.argv[1]}`) {
  const draw = hydrateLoops(
    { assembly_drawing_number: 'GI107', drawing_title: 'GIRT', revision: 'R0' },
    'x {{#drawings}}{{drawing_no}}/{{drawing_title}}{{/drawings}} y'
  );
  if (draw.drawings[0].drawing_no !== 'GI107' || draw.drawings[0].drawing_title !== 'GIRT')
    throw new Error('drawings self-wrap/alias failed');
  const imir = hydrateLoops(
    { mtc_tc_upload_ocr_confidence: 97, mtc_tc_upload_ocr_status: 'High' },
    'x {{#photos}}{{mtc_tc_upload_ocr_confidence}}{{/photos}} y'
  );
  if (imir.photos[0].mtc_tc_upload_ocr_confidence !== 97) throw new Error('imir photos failed');
  const doc = hydrateLoops({ document_number: 'NSPL/WPS/002' }, '{{#documents}}{{document_number}}{{/documents}}');
  if (doc.documents[0].document_number !== 'NSPL/WPS/002') throw new Error('documents self-wrap failed');
  console.log('hydrate-loops self-check OK');
}
