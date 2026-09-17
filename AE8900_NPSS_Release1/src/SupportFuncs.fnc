//============================================================
// Variable Definition
//============================================================

//============================================================
// Function Definitions
//============================================================
int FanDiameter() {
    real ht = 0.28; // hub-to-tip Ratio
    real D_fan_cnstrnt = 79; // inches
    int FanDiameterCheck = 0;

    // Calculate Fan Diameter
    real D_fan = sqrt((4*CmpFan.Fl_I.Aphy) / (PI*(1-ht**2)));// Fan Inlet Area: CmpFan.FL_I.Aphy or InEng.FL_O.Aphy;

    // Check Constraint
    if (D_fan > D_fan_cnstrnt){
        // Go to Step 1, Adjust FPRD
        cout << "D_fan = " << D_fan << endl;
        cout << "D_fan Constraint = " << D_fan_cnstrnt << endl;
        cout << endl;
        cout << "Fan Diameter Requirement Violated!   Adjust FPRD" << endl;
        cout << endl;

        //cout << "PROGRAM EXITING" << endl;
        //quit(); // Done by manually quitting and reguessing
    }
    else {
        cout << "Fan Diameter Constraint Passed!" << endl;
        cout << "D_fan = " << D_fan << endl;
        cout << endl;

        FanDiameterCheck = 1;
    }

    return FanDiameterCheck;
}

int EngineWeight() {
    real Weng = 300. * (1.6 - CmpFan.S_map.PRdes) + (120. * (CmpH.Fl_O.Pt/CmpFan.Fl_I.Pt)) + 100.0;
    real Leng = 0.78086 * (CmpH.Fl_O.Pt/CmpFan.Fl_I.Pt) + 75.2;
    real Weng_cnstrnt = 6500.0; // lbs

    if (Weng > Weng_cnstrnt){
        // Go to Step 1, Adjust FPRD, LPCPRD, or HPCPRD
        cout << "Weng = " << Weng << endl;
        cout << "Weng Constraint = " << Weng_cnstrnt << endl;
        cout << endl;

        cout << "Engine Weight Requirement Violated! Adjust FPRD, LPCPRD, or HPCPRD" << endl;
        cout << endl;
        //cout << "PROGRAM EXITING" << endl;
        //quit(); // Done by manually quitting and reguessing
    }
    else {
        cout << "Engine Weight Constraint Passed!" << endl;
        cout << "Weng = " << Weng << endl;
        cout << endl;
    }

    return EngineWeightCheck;
}

void CheckThrustRating(real NetThrust) {
    real Thrust_cnstrnt = 43.06; // lbf

    if (NetThrust < Thrust_cnstrnt){
        // Go to Step 1, Adjust FPRD, LPCPRD, or HPCPRD
        cout << "Fn = " << NetThrust << endl;
        cout << "Fn Constraint = " << Thrust_cnstrnt << endl;
        cout << endl;

        cout << "Engine Thrust Rating Requirement Violated! Adjust FPRD, LPCPRD, or HPCPRD" << endl;
        cout << endl;
        cout << "PROGRAM EXITING" << endl;
        quit(); // Done by manually quitting and reguessing
    }
    else {
        cout << "Engine Thrust Rating Constraint Passed!" << endl;
        cout << "Fn = " << NetThrust << endl;
        cout << endl;
    }

    //return EngineThrustCheck;
} // CheckThrustRating()



real InterpAtmosphere(real altitudes[], real target_alt, real AtmosType[]) {
    // Bounds check
    int n = altitudes.entries();
    if (target_alt < altitudes[0] || target_alt > altitudes[n - 1]) {
        cout << "Error: Altitude is out of valid range." << endl;
        cout << "PROGRAM EXITING..." << endl;
        quit();
    }

    // Find surrounding breakpoints
    int i;
    for (i = 0; i < n - 1; i++) {
        if (target_alt >= altitudes[i] && target_alt <= altitudes[i + 1]) {
            real alt_low   = altitudes[i];
            real alt_high  = altitudes[i + 1];
            real temp_low  = AtmosType[i];
            real temp_high = AtmosType[i + 1];

            // Linear interpolation
            real InterpTemp = temp_low + (temp_high - temp_low) * (target_alt - alt_low) / (alt_high - alt_low);
            //cout << "Interpolated Ambient Temp = " << InterpTemp << " deg R" << endl;
            return InterpTemp;
        }
    }
};

// Updated Engine Deck Function
void RunFullEngineDeck() {
    // Default to Save to Deck
    deckUpdate = 1;

    cout << "Running Engine Deck..." << endl;

    // Define Atmosphere dTs for FlightConditions()
    real altitudes[] = {0,5000,10000,15000,20000,25000,30000,35000,40000,45000};
    // Repeating final value for 45kft
    real HotdTs[]  = {44.0, 24.7, 4.90, -14.1, -33.5, -52.3, -71.3, -89.1, -103.74, -103.74};
    real ColddTs[] = {-119.0, -74.0, -74.0, -88.1, -105.1, -122.9, -141.36, -144.0, -144.0, -144.0};
    real TropdTs[] = {30.8, 11.43, -7.95, -27.32, -46.7, -66.0, -85.3, -104.6, -123.6, -123.0};
    string days[]  = {"STD"}; //{"STD","COLD","HOT","TROP"};
    real machs[] = {0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9};
    real ShaftLoads[] = {0.0}; //{0.0,1.0,2.0};
    real nominalNc = Nc_in;
    real percNcs[] = {0.80, 0.85, 0.90, 0.95, 1.0, 1.05, 1.10};
    real Ncs[] = {};
    int n;
    for (n=0;n<percNcs.entries();n++){
        Ncs.append( nominalNc*percNcs[n] ); 
    }
    int ia,im,id,is,in;
    real dts;
    string day;
    
    // Updates Ambient Tempurature
    for (id = 0; id<days.entries(); id++){

        for (is = 0; is<ShaftLoads.entries(); is++){
            ShH.HPX = ShaftLoads[is];

            // Update Altitude
            for (ia = 0; ia<altitudes.entries(); ia++){
                Amb.alt = altitudes[ia];

                if (days[id]=="STD"){
                    SPEC_DAY = "STD";
                    Amb.dTs = 0.0;
                }
                else if (days[id]=="COLD"){
                    SPEC_DAY = "COLD";
                    Amb.dTs = InterpAtmosphere(altitudes, Amb.alt, ColddTs);
                }
                else if (days[id]=="HOT"){
                    SPEC_DAY = "HOT";
                    Amb.dTs = InterpAtmosphere(altitudes, Amb.alt, HotdTs);
                }
                else if (days[id]=="TROP"){
                    SPEC_DAY = "TROP";
                    Amb.dTs = InterpAtmosphere(altitudes, Amb.alt, TropdTs);
                }
                else {
                    cout << "Requested Atmosphere Not Defined... Defaulting to STD" << endl;
                    Amb.dTs = 0.0;
                }

                // Update Mach Number
                for (im = 0; im<machs.entries(); im++){
                    Amb.MN = machs[im];

                    // Update Speed
                    for (in = 0; in<Ncs.entries(); in++){
                        Nc_in = Ncs[in];

                        .errHandler.clear();


                        // Run Engine Model
                        RunMaxThrust(); 

                        defErrs = .errHandler.errors;
                        if (defErrs.entries()>1){
                            system("pause");
                        }
                        //errHandler.ESIexists(2004299);


                        //RunThrottleHookDown(); 
                        //RunThrottleHookUp();
                    }

                }
            }
        }
    }
};



