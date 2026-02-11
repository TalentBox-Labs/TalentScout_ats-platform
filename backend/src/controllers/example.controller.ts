import { Request, Response } from 'express';

// Example controller structure
export class ExampleController {
  
  // GET all items
  async getAll(req: Request, res: Response) {
    try {
      // Your logic here
      res.status(200).json({
        status: 'success',
        data: []
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        message: 'Server error'
      });
    }
  }

  // GET single item
  async getById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      // Your logic here
      res.status(200).json({
        status: 'success',
        data: { id }
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        message: 'Server error'
      });
    }
  }

  // CREATE new item
  async create(req: Request, res: Response) {
    try {
      const data = req.body;
      // Your logic here
      res.status(201).json({
        status: 'success',
        data
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        message: 'Server error'
      });
    }
  }

  // UPDATE item
  async update(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const data = req.body;
      // Your logic here
      res.status(200).json({
        status: 'success',
        data: { id, ...data }
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        message: 'Server error'
      });
    }
  }

  // DELETE item
  async delete(req: Request, res: Response) {
    try {
      const { id } = req.params;
      // Your logic here
      res.status(200).json({
        status: 'success',
        message: 'Deleted successfully'
      });
    } catch (error) {
      res.status(500).json({
        status: 'error',
        message: 'Server error'
      });
    }
  }
}

export default new ExampleController();
