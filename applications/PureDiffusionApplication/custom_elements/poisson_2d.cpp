//   
//   Project Name:        Kratos       
//   Last modified by:    $Author: it's me! $
//   Date:                $Date: 2008-08-08 23:58:38 $
//   Revision:            $Revision: 1.0 $
//
//

// Project includes 
#include "includes/define.h"
#include "custom_elements/poisson_2d.h"
#include "pure_diffusion_application.h"
#include "utilities/math_utils.h"
#include "utilities/geometry_utilities.h" 

namespace Kratos
{
	


	//************************************************************************************
	//************************************************************************************
	Poisson2D::Poisson2D(IndexType NewId, GeometryType::Pointer pGeometry)
		: Element(NewId, pGeometry)
	{		
		// DO NOT ADD DOFS HERE!!!
	}

	//************************************************************************************
	//************************************************************************************
	Poisson2D::Poisson2D(IndexType NewId, GeometryType::Pointer pGeometry, PropertiesType::Pointer pProperties)
		: Element(NewId, pGeometry, pProperties)
	{
	}

	Element::Pointer Poisson2D::Create(IndexType NewId, NodesArrayType const& ThisNodes,  PropertiesType::Pointer pProperties) const
	{
		return Element::Pointer(new Poisson2D(NewId, GetGeometry().Create(ThisNodes), pProperties));
	}

	Poisson2D::~Poisson2D()
	{
	}

	//************************************************************************************
	//************************************************************************************
	void Poisson2D::CalculateLocalSystem(MatrixType& rLeftHandSideMatrix, VectorType& rRightHandSideVector, ProcessInfo& rCurrentProcessInfo)
	{
		KRATOS_TRY

		const double delta_t = rCurrentProcessInfo[DELTA_TIME];
		boost::numeric::ublas::bounded_matrix<double,3,3> msMassFactors = 1.0 / 3.0 * IdentityMatrix(3, 3);
		boost::numeric::ublas::bounded_matrix<double,3,2> msDN_DX;  //gradients matrix 
		boost::numeric::ublas::bounded_matrix<double,2,2> msD;  //conductivity matrix 
		msD = ZeroMatrix(2,2); //initializing the matrix as zero
  		array_1d<double,3> msN; //dimension = number of nodes . Position of the gauss point 
		array_1d<double,3> ms_temp; //dimension = number of nodes . . since we are using a residualbased approach 

		const unsigned int number_of_points = GetGeometry().size();

		if(rLeftHandSideMatrix.size1() != number_of_points)
			rLeftHandSideMatrix.resize(number_of_points,number_of_points,false); //resizing the system in case it does not have the right size 

		if(rRightHandSideVector.size() != number_of_points)
			rRightHandSideVector.resize(number_of_points,false);

		//getting data for the given geometry
		double Area;
		GeometryUtils::CalculateGeometryData(GetGeometry(), msDN_DX, msN, Area); //asking for gradients and other info 

		//reading properties and conditions
		double permittivity = GetProperties()[CONDUCTIVITY];
		msD(0,0)=permittivity;
		msD(1,1)=permittivity;
		double density = GetProperties()[DENSITY];
		double specific_heat = GetProperties()[SPECIFIC_HEAT];
		
		// main loop
		// LHS
		//const GeometryType::IntegrationPointsArrayType& integration_points = GetGeometry().IntegrationPoints();

		noalias(rLeftHandSideMatrix) = prod(msDN_DX,Matrix(prod(msD,trans(msDN_DX))));  // Bt D B

		// Inertia terms
		// LHS += bdf*M
		noalias(rLeftHandSideMatrix) += (density * specific_heat / delta_t) * msMassFactors;

		// RHS
		// No source terms
		noalias(rRightHandSideVector) = 0 * rRightHandSideVector;
		
		// Inertia terms (Backward Euler)
		for(unsigned int iii = 0; iii<number_of_points; iii++)
			ms_temp[iii] = GetGeometry()[iii].FastGetSolutionStepValue(TEMPERATURE,1);
		noalias(rRightHandSideVector) += (density * specific_heat / delta_t) * prod(msMassFactors, ms_temp);

		//subtracting the dirichlet term
		// RHS -= LHS*DUMMY_UNKNOWNs
		for(unsigned int iii = 0; iii<number_of_points; iii++)
			ms_temp[iii] = GetGeometry()[iii].FastGetSolutionStepValue(TEMPERATURE);
		noalias(rRightHandSideVector) -= prod(rLeftHandSideMatrix,ms_temp);
		
		rLeftHandSideMatrix *= Area;
		rRightHandSideVector *= Area;
		
		KRATOS_CATCH("");
	}

	//************************************************************************************
	//************************************************************************************
	void Poisson2D::CalculateRightHandSide(VectorType& rRightHandSideVector, ProcessInfo& rCurrentProcessInfo)
	{
		KRATOS_THROW_ERROR(std::logic_error,  "method not implemented" , "");
	}	 

	//************************************************************************************
	//************************************************************************************
	// this subroutine calculates the nodal contributions for the explicit steps of the 
	// fractional step procedure
	void Poisson2D::InitializeSolutionStep(ProcessInfo& CurrentProcessInfo)
	{
		KRATOS_TRY

		KRATOS_CATCH("");
	}

	//************************************************************************************
	//************************************************************************************
	void Poisson2D::EquationIdVector(EquationIdVectorType& rResult, ProcessInfo& CurrentProcessInfo)
	{
		unsigned int number_of_nodes = GetGeometry().PointsNumber();
		if(rResult.size() != number_of_nodes)
			rResult.resize(number_of_nodes,false);	

		for (unsigned int i=0;i<number_of_nodes;i++)
				rResult[i] = GetGeometry()[i].GetDof(TEMPERATURE).EquationId();
	}

	//************************************************************************************
	//************************************************************************************
	  void Poisson2D::GetDofList(DofsVectorType& ElementalDofList,ProcessInfo& CurrentProcessInfo)
	{
		unsigned int number_of_nodes = GetGeometry().PointsNumber();
		if(ElementalDofList.size() != number_of_nodes)
			ElementalDofList.resize(number_of_nodes);	

		for (unsigned int i=0;i<number_of_nodes;i++)
			ElementalDofList[i] = GetGeometry()[i].pGetDof(TEMPERATURE);

	}



} // Namespace Kratos
