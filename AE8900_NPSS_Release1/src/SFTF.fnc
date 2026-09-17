//============================================================
// Variable Definition
//============================================================
real MaxThrust;
real ThrustTarget;
real PercentFn;
int deckUpdate = 1;

//============================================================
//  NPSS Independents
//============================================================
Independent Des_BPR { 
	varName = "SpltFan.BPR";
}

Independent Burner_FAR {
	varName = "BrnPri.FAR";
}

Independent Des_Airflow {
	varName = "Amb.W";
}


//============================================================
//  NPSS Dependents and Constraints
//============================================================
Dependent Des_T41 {
 	eq_lhs = "TrbH.FS41.Tt";
	eq_rhs = "2750.0";
}

Dependent Des_Extraction_Ratio { 
	eq_lhs = "D015.Fl_O.Pt/D070.Fl_O.Pt"; //Change for single 
	eq_rhs = "1.1";
}
	
Dependent Des_Thrust { 
	eq_lhs = "Eng.Fn";
	eq_rhs = "5500.0"; // Fn TOC
}

Dependent Max_T4_TO { 
 	eq_lhs = "BrnPri.Fl_O.Tt";
	eq_rhs = "3250.0";
}  

Dependent MaxTO_T41 {
	eq_lhs = "TrbH.FS41.Tt";
	eq_rhs = "3000.0"; 
}
  
Dependent MaxCont_T41 {
	eq_lhs = "TrbH.FS41.Tt";
	eq_rhs = "2690.0"; 
}
  
Dependent TargetFn {
	eq_lhs = "Eng.Fn";
	eq_rhs = "ThrustTarget"; 
}

Dependent Des_T4 {
	eq_lhs = "BrnPri.Fl_O.Tt";
	eq_rhs = "3050.0";
}

// ==============================================================================
// RunMaxT4
// ==============================================================================
void RunMaxT4() { 
	autoSolverSetup(); 
	solver.addIndependent ( "Burner_FAR" );
	solver.addDependent ( "Max_T4_TO" );
	
	run(); ++CASE;

} // RunMaxT4

// ==============================================================================
// RunMaxThrust
// ==============================================================================
void RunMaxThrust() {
	cout << "Mach = " << Amb.MN << "   Alt = " << Amb.alt << "    dTs = " << Amb.dTs << endl; 
	autoSolverSetup();
	solver.addIndependent("Burner_FAR");
	
	if (Amb.alt <10000) {
		solver.addDependent("MaxTO_T41");
	} else {
		solver.addDependent("MaxCont_T41");
	}
	
	run(); CASE++;
	MaxThrust = Eng.Fn;
	if ( BrnPri.Fl_O.Tt > 3250 ){ // Using Max Take Off Tt4
		Limit_Flag = "TT4";
	}
	else {
		Limit_Flag = "NONE";
	}
	//cout << "MaxThrust = " << MaxThrust << endl;
}

// ==============================================================================
// RunPartThrust
// ==============================================================================
void RunPartThrust() {
	autoSolverSetup();
	solver.addIndependent("Burner_FAR");
	solver.addDependent("TargetFn");
	ThrustTarget = PercentFn*MaxThrust;
	run();
	CASE++;
}

// ==============================================================================
// RunThrottleHookDown
// ==============================================================================
void RunThrottleHookDown() {
	PercentFn = 1.0; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.9; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.8; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.7; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.6; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.5; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.4; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.3; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.2; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.1; RunPartThrust(); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
}

// ==============================================================================
// RunThrottleHookUp
// ==============================================================================
void RunThrottleHookUp() {
	// Run engine back up to max power for next condition
	PercentFn = 0.1; RunPartThrust();
	PercentFn = 0.2; RunPartThrust();
	PercentFn = 0.3; RunPartThrust();
	PercentFn = 0.4; RunPartThrust();
	PercentFn = 0.5; RunPartThrust();
	PercentFn = 0.6; RunPartThrust();
	PercentFn = 0.7; RunPartThrust();
	PercentFn = 0.8; RunPartThrust();
	PercentFn = 0.9; RunPartThrust();
	PercentFn = 1.0; RunPartThrust();
}

// ==============================================================================
// RunEngDeck
// ==============================================================================
void RunEngDeck() {
	Amb.alt=0; Amb.MN = 0.00; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=0; Amb.MN = 0.10; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=0; Amb.MN = 0.20; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=0; Amb.MN = 0.25; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=0; Amb.MN = 0.30; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=0; Amb.MN = 0.35; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=0; Amb.MN = 0.30; RunMaxThrust();
	Amb.alt=0; Amb.MN = 0.20; RunMaxThrust();
	Amb.alt=0; Amb.MN = 0.10; RunMaxThrust();
	Amb.alt=0; Amb.MN = 0.00; RunMaxThrust();

	Amb.alt=5000; Amb.MN = 0.00; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=5000; Amb.MN = 0.10; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=5000; Amb.MN = 0.20; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=5000; Amb.MN = 0.25; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=5000; Amb.MN = 0.30; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=5000; Amb.MN = 0.35; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=5000; Amb.MN = 0.40; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=5000; Amb.MN = 0.45; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=5000; Amb.MN = 0.40; RunMaxThrust();
	Amb.alt=5000; Amb.MN = 0.30; RunMaxThrust();
	Amb.alt=5000; Amb.MN = 0.20; RunMaxThrust();
	Amb.alt=5000; Amb.MN = 0.10; RunMaxThrust();

	Amb.alt=10000; Amb.MN = 0.10; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.20; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.25; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.30; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.35; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.40; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.45; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.50; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=10000; Amb.MN = 0.55; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=10000; Amb.MN = 0.50; RunMaxThrust();
	Amb.alt=10000; Amb.MN = 0.40; RunMaxThrust();
	Amb.alt=10000; Amb.MN = 0.30; RunMaxThrust();
	Amb.alt=10000; Amb.MN = 0.25; RunMaxThrust();

	Amb.alt=15000; Amb.MN = 0.25; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.30; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.35; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.40; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.45; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.50; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.55; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.60; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.65; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=15000; Amb.MN = 0.70; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=15000; Amb.MN = 0.60; RunMaxThrust();
	Amb.alt=15000; Amb.MN = 0.50; RunMaxThrust();
	Amb.alt=15000; Amb.MN = 0.40; RunMaxThrust();

	Amb.alt=20000; Amb.MN = 0.40; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.45; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.50; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.55; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.60; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.65; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.70; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.75; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.80; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=20000; Amb.MN = 0.85; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=20000; Amb.MN = 0.75; RunMaxThrust();
	Amb.alt=20000; Amb.MN = 0.65; RunMaxThrust();
	Amb.alt=20000; Amb.MN = 0.55; RunMaxThrust();
	Amb.alt=20000; Amb.MN = 0.45; RunMaxThrust();

	Amb.alt=25000; Amb.MN = 0.45; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=25000; Amb.MN = 0.50; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=25000; Amb.MN = 0.55; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();	
	Amb.alt=25000; Amb.MN = 0.60; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=25000; Amb.MN = 0.65; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=25000; Amb.MN = 0.70; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=25000; Amb.MN = 0.75; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=25000; Amb.MN = 0.80; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=25000; Amb.MN = 0.85; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=25000; Amb.MN = 0.75; RunMaxThrust(); 						
	Amb.alt=25000; Amb.MN = 0.65; RunMaxThrust(); 						
	Amb.alt=25000; Amb.MN = 0.55; RunMaxThrust(); 						

	Amb.alt=30000; Amb.MN = 0.55; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=30000; Amb.MN = 0.60; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=30000; Amb.MN = 0.65; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=30000; Amb.MN = 0.70; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=30000; Amb.MN = 0.75; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=30000; Amb.MN = 0.80; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=30000; Amb.MN = 0.85; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=30000; Amb.MN = 0.75; RunMaxThrust();
	Amb.alt=30000; Amb.MN = 0.65; RunMaxThrust();
	Amb.alt=30000; Amb.MN = 0.60; RunMaxThrust();

	Amb.alt=35000; Amb.MN = 0.60; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=35000; Amb.MN = 0.65; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=35000; Amb.MN = 0.70; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=35000; Amb.MN = 0.75; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=35000; Amb.MN = 0.80; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=35000; Amb.MN = 0.85; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=35000; Amb.MN = 0.75; RunMaxThrust();
	Amb.alt=35000; Amb.MN = 0.65; RunMaxThrust();
	Amb.alt=35000; Amb.MN = 0.60; RunMaxThrust();

	Amb.alt=39000; Amb.MN = 0.60; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=39000; Amb.MN = 0.65; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=39000; Amb.MN = 0.70; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=39000; Amb.MN = 0.75; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=39000; Amb.MN = 0.80; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=39000; Amb.MN = 0.85; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();

	Amb.alt=39000; Amb.MN = 0.75; RunMaxThrust();
	Amb.alt=39000; Amb.MN = 0.65; RunMaxThrust();
	Amb.alt=39000; Amb.MN = 0.60; RunMaxThrust();

	Amb.alt=43000; Amb.MN = 0.60; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=43000; Amb.MN = 0.65; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=43000; Amb.MN = 0.70; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=43000; Amb.MN = 0.75; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=43000; Amb.MN = 0.80; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
	Amb.alt=43000; Amb.MN = 0.85; RunMaxThrust(); RunThrottleHookDown(); RunThrottleHookUp();
}