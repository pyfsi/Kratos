//    |  /           |
//    ' /   __| _` | __|  _ \   __|
//    . \  |   (   | |   (   |\__ `
//   _|\_\_|  \__,_|\__|\___/ ____/
//                   Multi-Physics
//
//  License:         BSD License
//                   Kratos default license: kratos/license.txt
//
//  Main authors:    Miguel Masó Sotomayor
//


#if !defined(KRATOS_PURE_DIFFUSION_APPLICATION_VARIABLES_H_INCLUDED )
#define  KRATOS_PURE_DIFFUSION_APPLICATION_VARIABLES_H_INCLUDED

// System includes

// External includes

// Project includes
#include "includes/define.h"
#include "includes/kratos_application.h"
#include "includes/variables.h"

namespace Kratos
{
KRATOS_DEFINE_APPLICATION_VARIABLE( PURE_DIFFUSION_APPLICATION, double, POINT_HEAT_SOURCE)
KRATOS_DEFINE_APPLICATION_VARIABLE( PURE_DIFFUSION_APPLICATION, double, HEIGHT)
KRATOS_DEFINE_APPLICATION_VARIABLE( PURE_DIFFUSION_APPLICATION, double, PROJECTED_HEIGHT)
KRATOS_DEFINE_3D_APPLICATION_VARIABLE_WITH_COMPONENTS( PURE_DIFFUSION_APPLICATION, PROJECTED_VELOCITY )
}

#endif	/* KRATOS_PURE_DIFFUSION_APPLICATION_VARIABLES_H_INCLUDED */

