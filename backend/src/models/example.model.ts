// Example model structure
// Use this as a template for your data models

export interface ExampleModel {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface CreateExampleDTO {
  name: string;
  email: string;
}

export interface UpdateExampleDTO {
  name?: string;
  email?: string;
}

// Database operations would go here
// Example using raw queries or an ORM like Prisma/TypeORM
