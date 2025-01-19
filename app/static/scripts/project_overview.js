// File: static/scripts/project_overview.js

// For parent/child => vertical detail; for partner => horizontal detail
const verticalEnum = ['biological', 'step', 'adoptive', 'foster', 'other'];
const horizontalEnum = ['marriage', 'civil union', 'partnership'];

document.addEventListener('DOMContentLoaded', () => {
  const projectPage = document.getElementById('projectPage');
  if (!projectPage) return;

  const projectId = projectPage.dataset.projectId;
  const individualId = projectPage.dataset.individualId;

  // Right side
  const parentsList = document.getElementById('parentsList');
  const partnersList = document.getElementById('partnersList');
  const childrenList = document.getElementById('childrenList');
  const siblingsList = document.getElementById('siblingsList');
  // Left side
  const leftIndividualsList = document.getElementById('leftIndividualsList');

  /**
   * 1) fetchAllIndividuals => rebuild the entire left column
   */
  async function fetchAllIndividuals() {
    try {
      const resp = await fetch(`/api/individuals/?project_id=${projectId}`, {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!resp.ok) {
        throw new Error(`Cannot fetch individuals. HTTP ${resp.status}`);
      }
      const data = await resp.json();
      const array = data.individuals || [];

      leftIndividualsList.innerHTML = '';
      if (array.length === 0) {
        leftIndividualsList.innerHTML = '<li class="list-group-item text-muted">No individuals found.</li>';
        return;
      }
      array.forEach((ind) => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex align-items-center';
        li.setAttribute('draggable', 'true');
        li.style.cursor = 'pointer';
        li.dataset.individualId = ind.id;

        // name
        let displayName = 'Unknown';
        if (ind.primary_identity && ind.primary_identity.first_name) {
          displayName = `${ind.primary_identity.first_name} ${ind.primary_identity.last_name || ''}`.trim();
        }
        li.textContent = displayName;

        // click => go to that individual's page
        li.addEventListener('click', () => {
          window.location.href = `/individuals/?project_id=${projectId}&individual_id=${ind.id}`;
        });

        // dragstart => to form a relationship
        li.addEventListener('dragstart', (evt) => {
          evt.dataTransfer.setData('text/plain', ind.id);
          evt.dataTransfer.effectAllowed = 'move';
        });

        leftIndividualsList.appendChild(li);
      });
    } catch (err) {
      console.error('Error fetching all individuals for left column:', err);
      alert('Could not fetch individuals list.');
    }
  }

  /**
   * 2) fetchAndRenderRelationships => fill in parents/partners/children/siblings
   *    => exclude them from left side so they do not appear as duplicates
   */
  async function fetchAndRenderRelationships() {
    if (!individualId) return;
    try {
      const resp = await fetch(`/api/individuals/${individualId}?project_id=${projectId}`, {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!resp.ok) {
        throw new Error(`Cannot fetch relationships. HTTP ${resp.status}`);
      }
      const data = await resp.json();
      const indData = data.data;

      renderRelList(parentsList, indData.parents, 'parent');
      renderRelList(partnersList, indData.partners, 'partner');
      renderRelList(childrenList, indData.children, 'child');
      renderSiblingsList(indData.siblings);

      // Now exclude them from the left column
      excludeRelatedOnLeft(indData);
    } catch (err) {
      console.error('Error fetching relationships for the selected individual:', err);
      alert('An error occurred while fetching relationships.');
    }
  }

  function renderRelList(ul, relArray, relType) {
    ul.innerHTML = '';
    if (!relArray || relArray.length === 0) {
      ul.innerHTML = `<li class="list-group-item text-muted">No ${relType}s assigned.</li>`;
      return;
    }
    relArray.forEach((rel) => {
      const li = document.createElement('li');
      li.className = 'list-group-item d-flex flex-column';
      li.draggable = true;
      li.dataset.relationshipId = rel.relationship_id;
      li.dataset.individualId = rel.id;
      li.dataset.relationshipType = relType;

      // The top row with name + "Show Details"
      const topRow = document.createElement('div');
      topRow.className = 'd-flex justify-content-between align-items-center';

      // entire li click => goto that individual's page
      li.addEventListener('click', (e) => {
        if (e.target.classList.contains('show-details-btn')) {
          return;
        }
        window.location.href = `/individuals/?project_id=${projectId}&individual_id=${rel.id}`;
      });

      // name
      const nameSpan = document.createElement('span');
      const fn = rel.first_name || 'Unknown';
      const ln = rel.last_name || '';
      nameSpan.textContent = `${fn} ${ln}`.trim();

      const detailsBtn = document.createElement('button');
      detailsBtn.className = 'btn btn-sm btn-outline-secondary show-details-btn';
      detailsBtn.textContent = 'Show Details';
      detailsBtn.addEventListener('click', (evt) => {
        evt.stopPropagation();
        toggleRelDetails(li, rel, relType);
      });

      topRow.appendChild(nameSpan);
      topRow.appendChild(detailsBtn);
      li.appendChild(topRow);

      // drag
      li.addEventListener('dragstart', (evt) => {
        evt.dataTransfer.setData('application/x-relationship-id', rel.relationship_id);
        evt.dataTransfer.setData('text/plain', rel.id);
        evt.dataTransfer.effectAllowed = 'move';
      });

      ul.appendChild(li);
    });
  }

  function renderSiblingsList(siblings) {
    siblingsList.innerHTML = '';
    if (!siblings || siblings.length === 0) {
      siblingsList.innerHTML = '<li class="list-group-item text-muted">No siblings assigned.</li>';
      return;
    }
    siblings.forEach((sib) => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      const fn = sib.first_name || 'Unknown';
      const ln = sib.last_name || '';
      li.textContent = `${fn} ${ln} (ID: ${sib.id})`;
      li.style.cursor = 'pointer';
      li.addEventListener('click', () => {
        window.location.href = `/individuals/?project_id=${projectId}&individual_id=${sib.id}`;
      });
      siblingsList.appendChild(li);
    });
  }

  /**
   * exclude any used individuals from the left + exclude the selected individual
   */
  function excludeRelatedOnLeft(indData) {
    const usedIds = [];
    // exclude the selected
    const selectedId = parseInt(indData.id, 10);
    usedIds.push(selectedId);

    // gather parents, partners, children
    [...(indData.parents || []), ...(indData.partners || []), ...(indData.children || [])]
      .forEach(r => usedIds.push(parseInt(r.id, 10)));

    const items = leftIndividualsList.querySelectorAll('li.list-group-item');
    items.forEach(item => {
      const indivId = parseInt(item.dataset.individualId, 10);
      if (usedIds.includes(indivId)) {
        item.style.display = 'none';
      } else {
        item.style.display = 'flex'; // or 'list-item'
      }
    });
  }

  // Relationship drop targets: parents/partners/children
  [parentsList, partnersList, childrenList].forEach(ul => {
    ul.addEventListener('dragover', (e) => e.preventDefault());
    ul.addEventListener('drop', async (e) => {
      e.preventDefault();
      if (!individualId) return;
      const existingRelId = e.dataTransfer.getData('application/x-relationship-id');
      const draggedId = parseInt(e.dataTransfer.getData('text/plain'), 10);
      const newRelType = ul.dataset.relationshipType; // 'parent','partner','child'
      if (existingRelId) {
        await updateExistingRelationship(existingRelId, newRelType);
      } else {
        await createRelationship(newRelType, draggedId);
      }
    });
  });

  // Dropping onto left => remove that relationship
  leftIndividualsList.addEventListener('dragover', (e) => e.preventDefault());
  leftIndividualsList.addEventListener('drop', async (e) => {
    e.preventDefault();
    const relId = e.dataTransfer.getData('application/x-relationship-id');
    if (!relId) return;
    await removeRelationship(relId);
  });

  async function createRelationship(relType, draggedId) {
    if (!individualId) return;
    const selectedId = parseInt(individualId, 10);

    let indiv_id, rel_id, detail;
    if (relType === 'child') {
      // selected is the parent
      indiv_id = selectedId;
      rel_id = draggedId;
      relType = 'parent';
      detail = 'biological';
    } else if (relType === 'parent') {
      // dragged is the parent
      indiv_id = draggedId;
      rel_id = selectedId;
      detail = 'biological';
    } else if (relType === 'partner') {
      indiv_id = selectedId;
      rel_id = draggedId;
      detail = 'marriage';
    } else {
      alert(`Unknown relationship type: ${relType}`);
      return;
    }

    const payload = {
      individual_id: indiv_id,
      related_id: rel_id,
      initial_relationship: relType,
      relationship_detail: detail
    };
    try {
      const resp = await fetch(`/api/relationships/?project_id=${projectId}`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!resp.ok) {
        const errData = await resp.json();
        alert(errData.error || 'Failed to create relationship.');
        return;
      }
      alert('Relationship created successfully!');
      // re-fetch left list + right relationships
      await fetchAllIndividuals();
      await fetchAndRenderRelationships();
    } catch (err) {
      console.error('Error creating relationship:', err);
      alert('An error occurred creating the relationship.');
    }
  }

  async function updateExistingRelationship(relationshipId, newRelType) {
    let initial_relationship, relationship_detail;
    if (newRelType === 'child') {
      initial_relationship = 'parent';
      relationship_detail = 'biological';
    } else if (newRelType === 'parent') {
      initial_relationship = 'parent';
      relationship_detail = 'biological';
    } else if (newRelType === 'partner') {
      initial_relationship = 'partner';
      relationship_detail = 'marriage';
    } else {
      alert(`Unknown relationship type: ${newRelType}`);
      return;
    }
    try {
      const url = `/api/relationships/${relationshipId}?project_id=${projectId}`;
      const resp = await fetch(url, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ initial_relationship, relationship_detail })
      });
      if (!resp.ok) {
        const err = await resp.json();
        alert(err.error || 'Failed to update relationship.');
        return;
      }
      alert('Relationship updated successfully!');
      await fetchAllIndividuals();
      await fetchAndRenderRelationships();
    } catch (err) {
      console.error('Error updating relationship:', err);
      alert('An error occurred updating relationship.');
    }
  }

  async function removeRelationship(relationshipId) {
    try {
      const url = `/api/relationships/${relationshipId}?project_id=${projectId}`;
      const resp = await fetch(url, {
        method: 'DELETE',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      if (!resp.ok) {
        const err = await resp.json();
        alert(err.error || 'Failed to delete relationship.');
        return;
      }
      alert('Relationship deleted successfully.');
      await fetchAllIndividuals();
      await fetchAndRenderRelationships();
    } catch (err) {
      console.error('Error removing relationship:', err);
      alert('An error occurred removing that relationship.');
    }
  }

  async function toggleRelDetails(li, rel, relationshipType) {
    const existing = li.querySelector('.rel-details-collapse');
    if (existing) {
      existing.remove();
      return;
    }

    const detailsDiv = document.createElement('div');
    detailsDiv.className = 'rel-details-collapse mt-2 p-2 border';

    let dateFields = '';
    if (relationshipType === 'partner') {
      const uDate = rel.union_date || '';
      const dDate = rel.dissolution_date || '';
      dateFields = `
        <div class="mb-3">
          <label class="form-label">Union Date</label>
          <input type="date" class="form-control" name="union_date" value="${uDate}">
        </div>
        <div class="mb-3">
          <label class="form-label">Dissolution Date</label>
          <input type="date" class="form-control" name="dissolution_date" value="${dDate}">
        </div>
      `;
    }

    const isPartner = (relationshipType === 'partner');
    const enumOptions = isPartner ? horizontalEnum : verticalEnum;
    const relDetail = rel.relationship_detail || '';
    let detailSelect = `
      <label class="form-label">Relationship Detail</label>
      <select name="relationship_detail" class="form-select mb-3">
    `;
    enumOptions.forEach(opt => {
      detailSelect += `<option value="${opt}"${relDetail === opt ? ' selected' : ''}>${opt}</option>`;
    });
    detailSelect += '</select>';

    const notesVal = rel.notes || '';
    const notesField = `
      <label class="form-label">Notes</label>
      <textarea class="form-control mb-3" name="notes" rows="2">${notesVal}</textarea>
    `;

    detailsDiv.innerHTML = `
      ${detailSelect}
      ${dateFields}
      ${notesField}
      <button class="btn btn-sm btn-primary me-2">Save</button>
      <button class="btn btn-sm btn-secondary" type="button">Cancel</button>
      <div class="mt-3" id="unionChildrenContainer"></div>
    `;
    li.appendChild(detailsDiv);

//    // For partner => show "Children of This Union" read-only
//    if (relationshipType === 'partner') {
//      const container = detailsDiv.querySelector('#unionChildrenContainer');
//      container.innerHTML = `<p class="text-muted">Loading children of this union...</p>`;
//      try {
//        const [selData, partnerData] = await Promise.all([
//          fetchOneIndividual(parseInt(individualId, 10)),
//          fetchOneIndividual(rel.id)
//        ]);
//        const selectedChildren = selData ? (selData.children || []) : [];
//        const partnerChildren = partnerData ? (partnerData.children || []) : [];
//        const usedIds = new Set();
//        const unionList = [];
//
//        selectedChildren.forEach(ch => {
//          if (!usedIds.has(ch.id)) {
//            usedIds.add(ch.id);
//            unionList.push(ch);
//          }
//        });
//        partnerChildren.forEach(ch => {
//          if (!usedIds.has(ch.id)) {
//            usedIds.add(ch.id);
//            unionList.push(ch);
//          }
//        });
//
//        if (unionList.length === 0) {
//          container.innerHTML = `<p class="text-muted">No children in this union.</p>`;
//        } else {
//          let html = `<h6>Children of This Union (read-only)</h6>
//          <ul class="list-group">`;
//          unionList.forEach(ch => {
//            const fn = ch.first_name || 'Unknown';
//            const ln = ch.last_name || '';
//            html += `<li class="list-group-item">${fn} ${ln} (ID: ${ch.id})</li>`;
//          });
//          html += `</ul>`;
//          container.innerHTML = html;
//        }
//      } catch (err) {
//        console.error('Error loading union children:', err);
//        container.innerHTML = `<p class="text-danger">Failed to load children for this union.</p>`;
//      }
//    }

    const saveBtn = detailsDiv.querySelector('.btn-primary');
    const cancelBtn = detailsDiv.querySelector('.btn-secondary');

    saveBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const relationship_detail = detailsDiv.querySelector('[name="relationship_detail"]').value;
      const notes = detailsDiv.querySelector('[name="notes"]').value;
      let union_date = null, dissolution_date = null;
      if (relationshipType === 'partner') {
        union_date = detailsDiv.querySelector('[name="union_date"]').value || null;
        dissolution_date = detailsDiv.querySelector('[name="dissolution_date"]').value || null;
      }
      await patchRelationship(rel.relationship_id, { relationship_detail, union_date, dissolution_date, notes });
      detailsDiv.remove();
    });
    cancelBtn.addEventListener('click', () => detailsDiv.remove());
  }

  async function patchRelationship(relId, updates) {
    try {
      const url = `/api/relationships/${relId}?project_id=${projectId}`;
      const resp = await fetch(url, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (!resp.ok) {
        const msg = await resp.json();
        alert(msg.error || 'Failed to update relationship.');
        return;
      }
      alert('Relationship updated successfully!');
      await fetchAllIndividuals();
      await fetchAndRenderRelationships();
    } catch (err) {
      console.error('Error patching relationship:', err);
      alert('An error occurred updating relationship.');
    }
  }

  async function fetchOneIndividual(indId) {
    const url = `/api/individuals/${indId}?project_id=${projectId}`;
    const resp = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!resp.ok) {
      return null;
    }
    const data = await resp.json();
    return data.data; // {parents, children, partners, siblings, etc.}
  }

  // On load => 1) fetchAllIndividuals 2) fetch relationships
  async function init() {
    await fetchAllIndividuals();
    if (individualId) {
      await fetchAndRenderRelationships();
    }
  }

  init();
});