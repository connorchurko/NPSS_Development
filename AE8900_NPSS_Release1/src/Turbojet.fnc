//============================================================
// Variable Definition
//============================================================
real MaxThrust;
real ThrustTarget;
real PercentFn;

int deckUpdate = 1;
string solverMode = "Speed"; //Temp: FAR->Tt4, Speed: FAR -> N

//============================================================
//  NPSS Independents
//============================================================
Independent Burner_FAR {
    varName = "BrnPri.FAR";
}

Independent Des_Airflow {
    varName = "Amb.W";
}

//============================================================
//  NPSS Dependents and Constraints
//============================================================
Dependent Des_T4 { // Target Design Tt41
 	eq_lhs = "BrnPri.Fl_O.Tt";
	eq_rhs = "2650.0"; // deg R (2200 deg F)
}

Dependent dep_CMD_N {
	eq_lhs = "CmpH.Nc";
	eq_rhs = "Nc_in"; // nominal value "Nc_in"
}

Dependent Des_Thrust { // Target Design Thrust
	eq_lhs = "Eng.Fn";
	eq_rhs = "200.0"; 
}

Dependent Max_T4 { // Tt4 Max Value (Material Limit)
    eq_lhs = "BrnPri.Fl_O.Tt";
    eq_rhs = "2685.0"; // deg R (2250 deg F)
}

Dependent TargetFn {
	eq_lhs = "Eng.Fn";
	eq_rhs = "ThrustTarget"; 
}

// ==============================================================================
// RunMaxT4
// ==============================================================================
void RunMaxT4() { 
	autoSolverSetup(); 
	solver.addIndependent( "Burner_FAR" );
	solver.addDependent( "Max_T4" );
	
	run(); 
	//CASE++;

} // RunMaxT4

// ==============================================================================
// RunMaxThrust
// ==============================================================================
void RunMaxThrust() {
	cout << "Mach = " << Amb.MN << "   Alt = " << Amb.alt << "    dTs = " << Amb.dTs << "    Nc_cmd = " << Nc_in << endl;
	autoSolverSetup();
	//printIndependents();
	//printDependents();

	//CmpH.NcDes = 50000.0; // Design Nc for Compressor
	if (solverMode=="Temp") {
		solver.addIndependent( "Burner_FAR" );
    	solver.addDependent( "Des_T4" );
	}
	if (solverMode=="Speed"){
		//cout << "Shaft Speed Solver" << endl;
		solver.addIndependent( "Burner_FAR" );
		solver.addDependent( "dep_CMD_N" );
	}
	
	
	run(); 
	CASE++;
	//pv.display();
	//printPride();
	MaxThrust = Eng.Fn;
	if ( BrnPri.Fl_O.Tt > 2651.0 ){ // Using Max Take Off Tt4
		Limit_Flag = "TT4";
	}
	else {
		Limit_Flag = "NONE";
	}
	//cout << "MaxThrust = " << MaxThrust << endl;
	if (deckUpdate == 1) {Decksheet.update(); pv.display();}
}

// ==============================================================================
// RunPartThrust
// ==============================================================================
void RunPartThrust(string throttleDir) {
	autoSolverSetup();
	solver.addIndependent("Burner_FAR");
	solver.addDependent("TargetFn");
	ThrustTarget = PercentFn*MaxThrust;
	run();
	
	if (throttleDir=="down"){
		CASE++;
	}
	

	if ( BrnPri.Fl_O.Tt > 2651.0 ){ // Using Max Take Off Tt4
		Limit_Flag = "TT4";
	}
	else {
		Limit_Flag = "NONE";
	}
}

// ==============================================================================
// RunThrottleHookDown
// ==============================================================================
void RunThrottleHookDown() {
	PercentFn = 1.0; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.9; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.8; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.7; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.6; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.5; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.4; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.3; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.2; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
	PercentFn = 0.1; RunPartThrust("down"); if (deckUpdate == 1) {Decksheet.update(); pv.display();}
	//cout << ThrustTarget << "    " << Eng.TSFC << endl;
}

// ==============================================================================
// RunThrottleHookUp
// ==============================================================================
void RunThrottleHookUp() {
	// Run engine back up to max power for next condition
	PercentFn = 0.1; RunPartThrust("up");
	PercentFn = 0.2; RunPartThrust("up");
	PercentFn = 0.3; RunPartThrust("up");
	PercentFn = 0.4; RunPartThrust("up");
	PercentFn = 0.5; RunPartThrust("up");
	PercentFn = 0.6; RunPartThrust("up");
	PercentFn = 0.7; RunPartThrust("up");
	PercentFn = 0.8; RunPartThrust("up");
	PercentFn = 0.9; RunPartThrust("up");
	PercentFn = 1.0; RunPartThrust("up");
}