(function () {
  const canvas = document.getElementById('renderCanvas');
  const engine = new BABYLON.Engine(canvas, true, {
    preserveDrawingBuffer: true,
    stencil: true,
    antialias: true,
    deterministicLockstep: false,
    powerPreference: 'high-performance',
  });

  // ---- Game State ----
  const ELEMENTS = ['pyro', 'hydro', 'electro', 'cryo'];
  const ELEMENT_COLORS = {
    pyro: new BABYLON.Color3(1.0, 0.35, 0.1),
    hydro: new BABYLON.Color3(0.2, 0.6, 1.0),
    electro: new BABYLON.Color3(0.7, 0.3, 1.0),
    cryo: new BABYLON.Color3(0.7, 0.9, 1.0),
    physical: new BABYLON.Color3(0.9, 0.9, 0.9),
  };

  const state = {
    renderScale: 1,
    hdrEnabled: true,
    pipeline: null,

    // Player/character
    character: null,
    cameraTarget: null,
    animationGroups: [],
    input: { forward: false, back: false, left: false, right: false, sprint: false, attack: false, dash: false, jump: false },
    moveSpeed: 7,
    sprintMultiplier: 1.6,
    dashSpeed: 20,
    dashCooldown: 0,
    verticalVelocity: 0,
    gravity: -32,
    onGround: true,

    // Stamina / Energy
    stamina: 100,
    maxStamina: 100,
    staminaDrainSprintPerSec: 20,
    staminaCostDash: 20,
    staminaCostJump: 12,
    staminaRegenPerSec: 18,
    staminaRegenDelay: 0.8,
    staminaRegenDelayTimer: 0,

    // Party & abilities per member
    party: [
      { name: 'A', element: 'pyro' },
      { name: 'B', element: 'hydro' },
      { name: 'C', element: 'electro' },
      { name: 'D', element: 'cryo' },
    ],
    members: [
      { energy: 0, maxEnergy: 100, eCd: 0, eCdMax: 8, qCd: 0, qCdMax: 12 },
      { energy: 0, maxEnergy: 100, eCd: 0, eCdMax: 8, qCd: 0, qCdMax: 12 },
      { energy: 0, maxEnergy: 100, eCd: 0, eCdMax: 8, qCd: 0, qCdMax: 12 },
      { energy: 0, maxEnergy: 100, eCd: 0, eCdMax: 8, qCd: 0, qCdMax: 12 },
    ],
    activeIndex: 0,
    attackCooldown: 0,
    infusion: null, // { element, timeLeft }

    // Enemies
    enemies: [], // { mesh, health, maxHealth, status: { element, timeLeft }, effects: [] }
    lockedEnemy: null,
  };

  // ---- Utility ----
  function clamp01(v) { return Math.max(0, Math.min(1, v)); }
  function lerp(a, b, t) { return a + (b - a) * t; }

  function setHardwareScalingFor4K(scale) {
    engine.setHardwareScalingLevel(1 / (window.devicePixelRatio * scale));
    document.getElementById('resLabel').textContent = `${Math.round(window.innerWidth * window.devicePixelRatio * scale)}x${Math.round(window.innerHeight * window.devicePixelRatio * scale)}`;
  }

  function activeMember() { return state.members[state.activeIndex]; }
  function activeElement() { return state.party[state.activeIndex].element; }

  // ---- Scene ----
  function createScene() {
    const scene = new BABYLON.Scene(engine);
    scene.useRightHandedSystem = true;
    scene.autoClear = true;
    scene.createDefaultLight(true);

    // Environment
    scene.environmentIntensity = 1.0;
    scene.gravity = new BABYLON.Vector3(0, state.gravity, 0);

    const env = scene.createDefaultEnvironment({
      createSkybox: true,
      skyboxSize: 2000,
      enableGroundShadow: true,
      groundSize: 2000,
    });

    // Rendering pipeline
    state.pipeline = new BABYLON.DefaultRenderingPipeline('default', state.hdrEnabled, scene, scene.cameras);
    state.pipeline.samples = 4;
    state.pipeline.bloomEnabled = true;
    state.pipeline.bloomThreshold = 0.7;
    state.pipeline.bloomWeight = 0.35;
    state.pipeline.bloomKernel = 64;
    state.pipeline.imageProcessingEnabled = true;
    state.pipeline.imageProcessing.contrast = 1.05;
    state.pipeline.imageProcessing.exposure = 1.1;
    state.pipeline.sharpenEnabled = true;

    // Camera
    state.cameraTarget = new BABYLON.TransformNode('cameraTarget', scene);
    const camera = new BABYLON.FollowCamera('follow', new BABYLON.Vector3(0, 2, -6), scene);
    camera.lockedTarget = state.cameraTarget;
    camera.radius = 6.5;
    camera.heightOffset = 2.2;
    camera.rotationOffset = 180;
    camera.cameraAcceleration = 0.05;
    camera.maxCameraSpeed = 20;

    // Lights
    const hemi = new BABYLON.HemisphericLight('hemi', new BABYLON.Vector3(0.4, 1, 0.2), scene);
    hemi.intensity = 0.85;

    const dir = new BABYLON.DirectionalLight('dir', new BABYLON.Vector3(-0.5, -1, 0.4), scene);
    dir.position = new BABYLON.Vector3(30, 60, -30);
    dir.intensity = 2.2;
    const shadowGen = new BABYLON.ShadowGenerator(4096, dir);
    shadowGen.usePercentageCloserFiltering = true;
    shadowGen.bias = 0.0005;

    // Ground
    const ground = BABYLON.MeshBuilder.CreateGround('ground', { width: 2000, height: 2000, subdivisions: 64 }, scene);
    const groundMat = new BABYLON.PBRMaterial('groundMat', scene);
    groundMat.albedoColor = new BABYLON.Color3(0.28, 0.3, 0.32);
    groundMat.roughness = 0.8;
    ground.material = groundMat;
    ground.receiveShadows = true;

    // Character (placeholder)
    const characterRoot = new BABYLON.TransformNode('characterRoot', scene);
    BABYLON.SceneLoader.ImportMesh('', 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/CesiumMan/glTF/', 'CesiumMan.gltf', scene, (meshes, particleSystems, skeletons, animationGroups) => {
      const rootMesh = new BABYLON.TransformNode('hero', scene);
      meshes.forEach(m => {
        if (m.material && m.material.getClassName && m.material.getClassName() === 'PBRMaterial') {
          m.material.maxSimultaneousLights = 8;
        }
        m.receiveShadows = true;
        shadowGen.addShadowCaster(m, true);
        m.parent = rootMesh;
        m.scaling.scaleInPlace(1.2);
      });
      rootMesh.parent = characterRoot;
      rootMesh.position = new BABYLON.Vector3(0, 0, 0);

      state.character = rootMesh;
      state.animationGroups = animationGroups || [];
      state.animationGroups.forEach(ag => ag.start(true));

      state.cameraTarget.parent = state.character;
      state.cameraTarget.position = new BABYLON.Vector3(0, 1.6, 0);
    });

    // Enemies
    spawnEnemy(scene, new BABYLON.Vector3(6, 0, 6), 'hydro');
    spawnEnemy(scene, new BABYLON.Vector3(-8, 0, 3), 'pyro');
    spawnEnemy(scene, new BABYLON.Vector3(2, 0, -10), 'electro');

    // Input + UI
    attachInput(scene);
    bindUI();

    // Update loop
    scene.onBeforeRenderObservable.add(() => {
      const dt = scene.getEngine().getDeltaTime() / 1000;
      updateCharacter(dt);
      updateEnemies(dt);
      updateUI(dt);
    });

    return scene;
  }

  // ---- Enemies ----
  function spawnEnemy(scene, position, element) {
    const mesh = BABYLON.MeshBuilder.CreateCapsule('enemy', { height: 2, radius: 0.5 }, scene);
    mesh.position.copyFrom(position);
    const mat = new BABYLON.PBRMaterial('enemyMat', scene);
    mat.albedoColor = ELEMENT_COLORS[element] || new BABYLON.Color3(0.8, 0.2, 0.2);
    mat.metallic = 0.0; mat.roughness = 0.6;
    mesh.material = mat;

    const enemy = {
      mesh,
      element,
      health: 300,
      maxHealth: 300,
      status: null, // { element, timeLeft }
      effects: [], // DOTs etc.
      frozen: false,
    };
    state.enemies.push(enemy);
  }

  function updateEnemies(dt) {
    for (const enemy of state.enemies) {
      // Effects ticking
      const remain = [];
      for (const eff of enemy.effects) {
        eff.timeLeft -= dt;
        eff.tickTimer -= dt;
        if (eff.tickTimer <= 0) {
          eff.tickTimer += eff.tickInterval;
          applyDamage(enemy, eff.tickDamage, eff.element, { isDot: true });
        }
        if (eff.timeLeft > 0) remain.push(eff);
      }
      enemy.effects = remain;

      // Expire status
      if (enemy.status) {
        enemy.status.timeLeft -= dt;
        if (enemy.status.timeLeft <= 0) enemy.status = null;
      }

      // Simple death fade
      if (enemy.health <= 0 && enemy.mesh.isEnabled()) {
        enemy.mesh.setEnabled(false);
      }
    }

    // Maintain lock-on validity
    if (state.lockedEnemy && (!state.lockedEnemy.mesh.isEnabled() || state.lockedEnemy.health <= 0)) {
      state.lockedEnemy = null;
    }
  }

  // ---- Combat ----
  function getFacingVectors() {
    const scene = engine.scenes[0];
    const camera = scene.activeCamera;
    const forward = new BABYLON.Vector3(
      Math.sin(BABYLON.Tools.ToRadians(camera.rotationOffset)),
      0,
      Math.cos(BABYLON.Tools.ToRadians(camera.rotationOffset))
    ).normalize();
    const right = new BABYLON.Vector3(forward.z, 0, -forward.x);
    return { forward, right };
  }

  function performNormalAttack() {
    if (!state.character || state.attackCooldown > 0) return;
    state.attackCooldown = 0.35;

    const baseDamage = 30;
    const attackRange = 2.5;
    const attackAngleCos = Math.cos(Math.PI / 3); // 60 degrees

    const pos = state.character.position.clone();
    const { forward } = getFacingVectors();

    const infusionElement = state.infusion?.element || 'physical';

    for (const enemy of state.enemies) {
      if (!enemy.mesh.isEnabled()) continue;
      const toEnemy = enemy.mesh.position.subtract(pos);
      const dist = toEnemy.length();
      if (dist > 3.0 + attackRange) continue;
      toEnemy.y = 0;
      const dir = toEnemy.normalize();
      if (BABYLON.Vector3.Dot(forward, dir) < attackAngleCos) continue;
      const damage = computeReactionDamage(enemy, baseDamage, infusionElement);
      applyDamage(enemy, damage, infusionElement);
      // Energy on hit
      const am = activeMember();
      am.energy = Math.min(am.maxEnergy, am.energy + 4);
    }

    // Small swipe VFX
    spawnHitVfx(state.character.position.add(forward.scale(1.2)), infusionElement);
  }

  function castSkillE() {
    const am = activeMember();
    if (am.eCd > 0) return;
    am.eCd = am.eCdMax;

    // Elemental melee wave
    const element = activeElement();
    state.infusion = { element, timeLeft: 6 };

    const baseDamage = 60;
    const pos = state.character.position.clone();
    const { forward } = getFacingVectors();
    for (const enemy of state.enemies) {
      if (!enemy.mesh.isEnabled()) continue;
      const toEnemy = enemy.mesh.position.subtract(pos);
      if (toEnemy.length() > 4.0) continue;
      const damage = computeReactionDamage(enemy, baseDamage, element);
      applyDamage(enemy, damage, element);
      applyElement(enemy, element, 8);
      const am2 = activeMember();
      am2.energy = Math.min(am2.maxEnergy, am2.energy + 8);
    }
    spawnHitVfx(state.character.position.add(forward.scale(1.8)), element);
  }

  function castBurstQ() {
    const am = activeMember();
    if (am.qCd > 0 || am.energy < am.maxEnergy) return;
    am.qCd = am.qCdMax;
    am.energy = 0;

    const element = activeElement();
    const baseDamage = 140;

    // AoE
    const pos = state.character.position.clone();
    for (const enemy of state.enemies) {
      if (!enemy.mesh.isEnabled()) continue;
      const dist = BABYLON.Vector3.Distance(enemy.mesh.position, pos);
      if (dist > 6.5) continue;
      const damage = computeReactionDamage(enemy, baseDamage, element, { isBurst: true });
      applyDamage(enemy, damage, element);
      applyElement(enemy, element, 10);
      // Add special DOT for electro burst
      if (element === 'electro') {
        enemy.effects.push({ element: 'electro', timeLeft: 4, tickInterval: 1, tickTimer: 1, tickDamage: 12 });
      }
    }
    spawnRingVfx(pos, element);
  }

  function computeReactionDamage(enemy, base, incomingElement, opts = {}) {
    if (!enemy.status || enemy.status.element === incomingElement) return base;
    const a = incomingElement, b = enemy.status.element;
    let mult = 1.0;
    let extra = 0;
    const setDot = (type, secs, tick, dmg) => enemy.effects.push({ element: type, timeLeft: secs, tickInterval: tick, tickTimer: tick, tickDamage: dmg });

    const pair = new Set([a, b]);
    if (pair.has('pyro') && pair.has('hydro')) {
      mult = 1.5;
    } else if (pair.has('pyro') && pair.has('cryo')) {
      mult = 1.6;
    } else if (pair.has('electro') && pair.has('hydro')) {
      mult = 1.2; setDot('electro', 4, 1, 8);
    } else if (pair.has('electro') && pair.has('cryo')) {
      mult = 1.2; // superconduct-like
    } else if (pair.has('pyro') && pair.has('electro')) {
      mult = 1.3; // overload-like
    } else if (pair.has('hydro') && pair.has('cryo')) {
      mult = 1.0; enemy.frozen = true; // frozen
    }
    return Math.floor(base * mult + extra);
  }

  function applyElement(enemy, element, duration) {
    enemy.status = { element, timeLeft: duration };
  }

  function applyDamage(enemy, amount, element, flags = {}) {
    if (enemy.frozen && element === 'pyro') {
      // break freeze for a small bonus
      amount = Math.floor(amount * 1.25);
      enemy.frozen = false;
    }
    enemy.health -= amount;
    if (enemy.health < 0) enemy.health = 0;
    // brief flash
    const m = enemy.mesh.material;
    if (m && m.albedoColor) {
      const orig = m.albedoColor.clone();
      m.albedoColor = BABYLON.Color3.White();
      setTimeout(() => { m.albedoColor = orig; }, 60);
    }
  }

  // ---- VFX (very simple) ----
  function spawnHitVfx(position, element) {
    const scene = engine.scenes[0];
    const s = BABYLON.MeshBuilder.CreateSphere('hit', { diameter: 0.8 }, scene);
    const m = new BABYLON.StandardMaterial('hitMat', scene);
    const c = ELEMENT_COLORS[element] || ELEMENT_COLORS.physical;
    m.emissiveColor = new BABYLON.Color3(c.r, c.g, c.b);
    m.diffuseColor = new BABYLON.Color3(0,0,0);
    s.material = m; s.position.copyFrom(position);
    s.scaling.scaleInPlace(0.3);
    const start = performance.now();
    scene.onBeforeRenderObservable.add(function vfx() {
      const t = (performance.now() - start) / 300;
      s.scaling.setAll(lerp(0.3, 1.5, t));
      m.alpha = 1 - t;
      if (t >= 1) { s.dispose(); scene.onBeforeRenderObservable.removeCallback(vfx); }
    });
  }

  function spawnRingVfx(position, element) {
    const scene = engine.scenes[0];
    const ring = BABYLON.MeshBuilder.CreateTorus('ring', { diameter: 0.5, thickness: 0.07 }, scene);
    ring.position.copyFrom(position);
    const m = new BABYLON.StandardMaterial('ringMat', scene);
    const c = ELEMENT_COLORS[element] || ELEMENT_COLORS.physical;
    m.emissiveColor = new BABYLON.Color3(c.r, c.g, c.b);
    m.alpha = 0.9; ring.material = m;
    const start = performance.now();
    scene.onBeforeRenderObservable.add(function ringFx() {
      const t = (performance.now() - start) / 600;
      ring.scaling.setAll(lerp(1, 8, t));
      m.alpha = 1 - t;
      if (t >= 1) { ring.dispose(); scene.onBeforeRenderObservable.removeCallback(ringFx); }
    });
  }

  // ---- Input ----
  function attachInput(scene) {
    window.addEventListener('keydown', (e) => {
      if (e.repeat) return;
      switch (e.code) {
        case 'KeyW': state.input.forward = true; break;
        case 'KeyS': state.input.back = true; break;
        case 'KeyA': state.input.left = true; break;
        case 'KeyD': state.input.right = true; break;
        case 'ShiftLeft': case 'ShiftRight': state.input.sprint = true; break;
        case 'Space': state.input.jump = true; break;
        case 'KeyE': castSkillE(); break;
        case 'KeyQ': castBurstQ(); break;
        case 'Tab': toggleLockOn(); e.preventDefault(); break;
        case 'Digit1': switchParty(0); break;
        case 'Digit2': switchParty(1); break;
        case 'Digit3': switchParty(2); break;
        case 'Digit4': switchParty(3); break;
      }
    });
    window.addEventListener('keyup', (e) => {
      switch (e.code) {
        case 'KeyW': state.input.forward = false; break;
        case 'KeyS': state.input.back = false; break;
        case 'KeyA': state.input.left = false; break;
        case 'KeyD': state.input.right = false; break;
        case 'ShiftLeft': case 'ShiftRight': state.input.sprint = false; break;
        case 'Space': state.input.jump = false; break;
      }
    });

    // Pointer lock and camera orbit via rotationOffset/heightOffset
    canvas.addEventListener('click', () => canvas.requestPointerLock?.());
    window.addEventListener('mousemove', (e) => {
      if (document.pointerLockElement !== canvas) return;
      const rotY = -e.movementX * 0.1;
      const rotX = -e.movementY * 0.05;
      const scene = engine.scenes[0];
      const camera = scene.activeCamera;
      camera.rotationOffset = (camera.rotationOffset + rotY) % 360;
      camera.heightOffset = BABYLON.Scalar.Clamp(camera.heightOffset + rotX * 0.05, 1.2, 4.0);
    });

    window.addEventListener('mousedown', (e) => {
      if (e.button === 0) { state.input.attack = true; performNormalAttack(); }
    });
    window.addEventListener('mouseup', (e) => {
      if (e.button === 0) state.input.attack = false;
    });
  }

  // ---- Movement / Character Update ----
  function updateCharacter(dt) {
    if (!state.character) return;

    // Facing vectors from camera
    const { forward, right } = getFacingVectors();

    // Movement input
    let move = new BABYLON.Vector3(0, 0, 0);
    if (state.input.forward) move.addInPlace(forward);
    if (state.input.back) move.subtractInPlace(forward);
    if (state.input.right) move.addInPlace(right);
    if (state.input.left) move.subtractInPlace(right);
    if (move.lengthSquared() > 0.0001) move.normalize();

    // Sprint / stamina drain
    let speed = state.moveSpeed;
    const isMoving = move.lengthSquared() > 0;
    const canSprint = state.stamina > 0.5 && state.input.sprint && isMoving;
    if (canSprint) {
      speed *= state.sprintMultiplier;
      state.stamina = Math.max(0, state.stamina - state.staminaDrainSprintPerSec * dt);
      state.staminaRegenDelayTimer = state.staminaRegenDelay;
    }

    // Dash on Space if not jumping and have stamina and cooldown <= 0
    if (state.input.jump && state.onGround && state.dashCooldown <= 0 && state.stamina >= state.staminaCostDash) {
      // Use as short dash + small hop
      const dashVec = move.lengthSquared() > 0 ? move : forward;
      state.character.position.addInPlace(dashVec.scale(state.dashSpeed * dt * 2.2));
      state.verticalVelocity = 6;
      state.onGround = false;
      state.stamina = Math.max(0, state.stamina - state.staminaCostDash);
      state.dashCooldown = 0.6;
      state.staminaRegenDelayTimer = state.staminaRegenDelay;
    }

    // Jump if on ground and enough stamina when pressing Space without dash condition
    if (state.input.jump && state.onGround && state.dashCooldown > 0 && state.stamina >= state.staminaCostJump) {
      state.verticalVelocity = 7.5;
      state.onGround = false;
      state.stamina = Math.max(0, state.stamina - state.staminaCostJump);
      state.staminaRegenDelayTimer = state.staminaRegenDelay;
    }

    // Apply horizontal displacement
    const displacement = move.scale(speed * dt);
    state.character.position.addInPlace(displacement);

    // Apply gravity
    state.verticalVelocity += state.gravity * dt;
    state.character.position.y += state.verticalVelocity * dt;
    if (state.character.position.y <= 0) {
      state.character.position.y = 0;
      state.verticalVelocity = 0;
      state.onGround = true;
    }

    // Rotate character toward move direction
    if (isMoving) {
      const targetYawDeg = Math.atan2(move.x, move.z) * 180 / Math.PI;
      const currentYawDeg = state.character.rotation.y * 180 / Math.PI;
      const newYaw = BABYLON.Scalar.LerpAngle(currentYawDeg, targetYawDeg, 0.2);
      state.character.rotation.y = newYaw * Math.PI / 180;
    }

    // Cooldowns/timers
    state.dashCooldown = Math.max(0, state.dashCooldown - dt);
    state.attackCooldown = Math.max(0, state.attackCooldown - dt);
    if (state.infusion) {
      state.infusion.timeLeft -= dt; if (state.infusion.timeLeft <= 0) state.infusion = null;
    }

    // Stamina regen
    if (state.staminaRegenDelayTimer > 0) state.staminaRegenDelayTimer -= dt;
    if (state.staminaRegenDelayTimer <= 0 && !state.input.sprint) {
      state.stamina = Math.min(state.maxStamina, state.stamina + state.staminaRegenPerSec * dt);
    }

    // Ability cooldowns per member
    for (const m of state.members) {
      m.eCd = Math.max(0, m.eCd - dt);
      m.qCd = Math.max(0, m.qCd - dt);
    }
  }

  // ---- Lock-on ----
  function toggleLockOn() {
    if (state.lockedEnemy) { state.lockedEnemy = null; return; }
    // Find nearest alive enemy
    let best = null, bestDist = Infinity;
    const pos = state.character?.position || new BABYLON.Vector3(0,0,0);
    for (const enemy of state.enemies) {
      if (!enemy.mesh.isEnabled() || enemy.health <= 0) continue;
      const d = BABYLON.Vector3.DistanceSquared(enemy.mesh.position, pos);
      if (d < bestDist) { bestDist = d; best = enemy; }
    }
    state.lockedEnemy = best;
  }

  // ---- UI ----
  function bindUI() {
    document.getElementById('btnMax').addEventListener('click', () => applyPreset('max'));
    document.getElementById('btnBalanced').addEventListener('click', () => applyPreset('balanced'));
    document.getElementById('btnPerformance').addEventListener('click', () => applyPreset('performance'));
    document.getElementById('btnToggleHDR').addEventListener('click', () => {
      state.hdrEnabled = !state.hdrEnabled;
      if (state.pipeline) state.pipeline.hdr = state.hdrEnabled;
    });

    document.getElementById('btnSkillE').addEventListener('click', castSkillE);
    document.getElementById('btnBurstQ').addEventListener('click', castBurstQ);

    // Party slot clicks
    document.querySelectorAll('.party-slot').forEach((el, i) => {
      el.addEventListener('click', () => switchParty(i));
    });
  }

  function switchParty(index) {
    if (index < 0 || index >= state.party.length) return;
    state.activeIndex = index;
    updatePartyUI();
  }

  function updateUI(dt) {
    // FPS
    document.getElementById('fps').textContent = String(Math.round(engine.getFps()));

    // Stamina / Energy bars
    const staminaFrac = clamp01(state.stamina / state.maxStamina);
    const staminaFill = document.getElementById('staminaFill');
    staminaFill.style.transform = `scaleX(${staminaFrac})`;

    const am = activeMember();
    const energyFrac = clamp01(am.energy / am.maxEnergy);
    const energyFill = document.getElementById('energyFill');
    energyFill.style.transform = `scaleX(${energyFrac})`;

    // Cooldowns text
    const cdE = document.getElementById('cdE');
    const cdQ = document.getElementById('cdQ');
    cdE.textContent = am.eCd > 0 ? String(Math.ceil(am.eCd)) : '0';
    cdQ.textContent = am.qCd > 0 ? String(Math.ceil(am.qCd)) : '0';

    // Disable buttons if not available
    const btnE = document.getElementById('btnSkillE');
    const btnQ = document.getElementById('btnBurstQ');
    btnE.disabled = am.eCd > 0;
    btnQ.disabled = am.qCd > 0 || am.energy < am.maxEnergy;

    // Lock-on label
    const lockLabel = document.getElementById('lockLabel');
    lockLabel.textContent = state.lockedEnemy ? `${state.lockedEnemy.element} (${Math.ceil(state.lockedEnemy.health)})` : 'None';

    // Party highlight
    updatePartyUI();
  }

  function updatePartyUI() {
    document.querySelectorAll('.party-slot').forEach((el, i) => {
      el.classList.toggle('active', i === state.activeIndex);
      const elem = state.party[i].element;
      el.style.outlineColor = `rgb(${ELEMENT_COLORS[elem].r*255}, ${ELEMENT_COLORS[elem].g*255}, ${ELEMENT_COLORS[elem].b*255})`;
    });
  }

  // ---- Quality presets ----
  function applyPreset(preset) {
    switch (preset) {
      case 'max':
        state.hdrEnabled = true;
        if (state.pipeline) state.pipeline.samples = 8;
        setHardwareScalingFor4K(1.25);
        break;
      case 'balanced':
        state.hdrEnabled = true;
        if (state.pipeline) state.pipeline.samples = 4;
        setHardwareScalingFor4K(1.0);
        break;
      case 'performance':
        state.hdrEnabled = false;
        if (state.pipeline) state.pipeline.samples = 1;
        setHardwareScalingFor4K(0.66);
        break;
    }
    if (state.pipeline) state.pipeline.hdr = state.hdrEnabled;
  }

  // ---- Bootstrap ----
  const scene = createScene();
  setHardwareScalingFor4K(1.0);

  engine.runRenderLoop(() => {
    scene.render();
  });

  window.addEventListener('resize', () => {
    engine.resize();
    setHardwareScalingFor4K(state.renderScale || 1.0);
  });
})();