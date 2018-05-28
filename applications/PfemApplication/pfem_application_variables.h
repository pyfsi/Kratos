//--------------------------------------------------------
//          ___  __                                      .
//  KRATOS | _ \/ _|___ _ __                             .
//         |  _/  _/ -_) '  \                            .  
//         |_| |_| \___|_|_|_| APPLICATION               .
//                                                       .    
//  License:(BSD)         PfemApplication/license.txt    .
//  Main authors:         Josep Maria Carbonell          .
//                        ..                             .
//--------------------------------------------------------
//
//   Project Name:        KratosPfemApplication     $
//   Created by:          $Author:      JMCarbonell $
//   Last modified by:    $Co-Author:               $
//   Date:                $Date:           May 2018 $
//   Revision:            $Revision:            0.0 $
//
//

#if !defined(KRATOS_PFEM_APPLICATION_VARIABLES_H_INCLUDED )
#define  KRATOS_PFEM_APPLICATION_VARIABLES_H_INCLUDED

// System includes

// External includes

// Project includes
#include "includes/cfd_variables.h"
#include "includes/kratos_flags.h"

#include "solid_mechanics_application_variables.h"

namespace Kratos
{
  ///@name Type Definitions
  ///@{
  ///@}

  ///@name Kratos Globals
  ///@{

  //Define Variables
  KRATOS_DEFINE_APPLICATION_VARIABLE( PFEM_APPLICATION, Vector, MATERIAL_PERCENT_COMPOSITION )
  KRATOS_DEFINE_APPLICATION_VARIABLE( PFEM_APPLICATION, double, PRESSURE_VELOCITY )
  KRATOS_DEFINE_APPLICATION_VARIABLE( PFEM_APPLICATION, double, PRESSURE_ACCELERATION )

  ///@}

}

#endif	// KRATOS_PFEM_APPLICATION_VARIABLES_H_INCLUDED defined
